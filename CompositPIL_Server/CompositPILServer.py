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
    # Scale
    scale_type = request.params["scale_type"]
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


    # Convert
    # *************************************************************************
    for file_path in image_files:
        # 変換元画像読み込み
        # -------------------------------------------------
        img = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)
        if img is None:  # ファイル読み込みチェック
            print("file open failed: {:s}".format(file_path))
            continue
        img_shape = img.shape

        # ついでに拡大
        if scale_type == "x2c-up" or scale_type == "x2c-down":
            img = cv2.resize(img, (img_shape[1]*2, img_shape[0]*2), interpolation=cv2.INTER_CUBIC)


        # Canny Convert
        # -------------------------------------------------
        canny_img = None  # Edgeイメージ格納先

        if canny_data["image_type"] == "BW":
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

        # 変換できなかった
        if canny_img is None:
            print("create image failed: {:s}".format(file_path))
            continue

        # 拡大したので縮小
        if scale_type == "x2c-down":
            canny_img = cv2.resize(canny_img, (img_shape[1], img_shape[0]), interpolation=cv2.INTER_CUBIC)


        # 出力先に保存
        # -------------------------------------------------
        print(canny_data)
        fname, ext = os.path.splitext(os.path.basename(file_path))
        if ext.upper() == ".PNG":
            output_file_path = os.path.join(output_dir, canny_data["output_prefix"] + fname) + ext
        else:
            output_file_path = os.path.join(output_dir, canny_data["output_prefix"] + fname) + ".png"  # 必ずpngで出力
        cv2.imwrite(output_file_path, canny_img)


    # 終了
    # *************************************************************************
    response.headers['Cache-Control'] = 'no-cache'
    return {'result':"Complete"}



# Server
# *****************************************************************************
@app.route('/')
def hello():
    return "hello!"

run(app, host='localhost', port=SERVER_PORT, reloader=True)
