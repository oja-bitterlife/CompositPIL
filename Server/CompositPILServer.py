from bottle import Bottle, run, request, response
import re, os, os.path, json
import cv2

# DEFINE
SERVER_PORT = 8080

app = Bottle()

# Utility
# *****************************************************************************
def to_bw(img):
    if img.ndim == 2:
        return img
    else:
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


# メインサービス
# *****************************************************************************
@app.route('/canny')
def canny_service():
    # 出力先
    output_dir = request.params["output_path"]
    # 変換パラメータ
    canny_data = json.loads(request.params["canny_data"])

    # 対象ファイルの検出
    # *************************************************************************
    image_files = set([])  # 見つけたファイル記録場所

    image_dir = os.path.dirname(canny_data["image_name"])
    image_file = os.path.basename(canny_data["image_name"])
    if image_file:  # ファイル名がちゃんと設定されていること
        regex_file = image_file.replace("#", "[0-9]")  # #は0-9として扱う

        # ファイルを全部確認
        for f in os.listdir(image_dir):

            # ファイルだけ調べる
            path = os.path.join(image_dir, f)
            if os.path.isfile(path):
                # #を置き換えてマッチするか
                match = re.match(regex_file + "$", f)
                if match:
                    image_files.add(path)  # マッチしたので記録

    # 出力先ディレクトリが無かったら作っておく
    if not os.path.exists(output_dir) and len(image_files) > 0:
        os.mkdir(output_dir)

    # Canny Convert
    # *************************************************************************
    for file_path in image_files:
        img = cv2.imread(file_path, -1)
        if img is None:  # ファイル読み込みチェック
            print("file open failed: {:s}".format(file_path))
            continue

        canny_img = None  # Edgeイメージ格納先

        if canny_data["image_type"] == "BW" or canny_data["image_type"] == "DEPTH":
            canny_img = cv2.Canny(to_bw(img), threshold1=canny_data["adjacent"], threshold2=canny_data["threshold"])
        elif canny_data["image_type"] == "RGB":
            img_rgba = cv2.split(img)
            canny_img_r = cv2.Canny(img_rgba[0], threshold1=canny_data["adjacent"], threshold2=canny_data["threshold"])
            canny_img_g = cv2.Canny(img_rgba[1], threshold1=canny_data["adjacent"], threshold2=canny_data["threshold"])
            canny_img_b = cv2.Canny(img_rgba[2], threshold1=canny_data["adjacent"], threshold2=canny_data["threshold"])
            # AにRGB全部まとめたものを
            img_tmp = cv2.addWeighted(canny_img_r, 1, canny_img_g, 1, 0)
            img_tmp = cv2.addWeighted(img_tmp, 1, canny_img_b, 1, 0)
            # 合成
            canny_img = cv2.merge((canny_img_b, canny_img_g, canny_img_r, img_tmp))
        elif canny_data["image_type"] == "ALPHA":
            img_rgba = cv2.split(img)
            if len(img_rgba) >= 4:  # アルファを使う
                bw_img = img_rgba[3]
            else:  # グレースケールで扱う
                bw_img = to_bw(img)
            # 二値化
            alpha_threshold = int(canny_data["alpha_threshold"] * 255)
            _, bin_img = cv2.threshold(bw_img, alpha_threshold, 255, cv2.THRESH_BINARY)
            canny_img = cv2.Canny(bin_img, threshold1=canny_data["adjacent"], threshold2=canny_data["threshold"])
        elif canny_data["image_type"] == "RGBA":
            img_rgba = cv2.split(img)
            # RGB部分
            canny_img_r = cv2.Canny(img_rgba[0], threshold1=canny_data["adjacent"], threshold2=canny_data["threshold"])
            canny_img_g = cv2.Canny(img_rgba[1], threshold1=canny_data["adjacent"], threshold2=canny_data["threshold"])
            canny_img_b = cv2.Canny(img_rgba[2], threshold1=canny_data["adjacent"], threshold2=canny_data["threshold"])
            # A部分
            if len(img_rgba) >= 4:
                alpha_threshold = int(canny_data["alpha_threshold"] * 255)
                _, bin_img = cv2.threshold(img_rgba[3], alpha_threshold, 255, cv2.THRESH_BINARY)
                canny_img_a = cv2.Canny(bin_img, threshold1=canny_data["adjacent"], threshold2=canny_data["threshold"])
                # 合成
                canny_img = cv2.merge((canny_img_b, canny_img_g, canny_img_r, canny_img_a))
            else:
                # A無しで合成
                canny_img = cv2.merge((canny_img_b, canny_img_g, canny_img_r))

        # 変換できなかった
        if canny_img is None:
            print("create image failed: {:s}".format(file_path))
            continue

        # 出力先に保存
        fname, ext = os.path.splitext(os.path.basename(file_path))
        if ext.upper() == ".PNG":
            output_file_path = os.path.join(output_dir, fname) + ext
        else:
            output_file_path = os.path.join(output_dir, fname) + ".png"  # 必ずpngで出力
        cv2.imwrite(output_file_path, canny_img)

    response.headers['Cache-Control'] = 'no-cache'
    return {'result':"Complete"}


@app.route('/')
def hello():
    return "hello!"

# Server
run(app, host='localhost', port=SERVER_PORT, reloader=True)
