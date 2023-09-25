from bottle import Bottle, run, request, response
import re, os, os.path
import cv2

app = Bottle()

@app.route('/')
def hello():
    return "hello!"

@app.route('/canny')
def canny():
    # 出力先
    output_dir = request.params["output_path"]

    # 対象ファイルの検出
    image_files = set([])  # 見つけたファイル記録場所

    image_names = ["image_name1", "image_name2", "image_name3"]
    for image_name in image_names:
        image_dir = os.path.dirname(request.params[image_name])
        image_file = os.path.basename(request.params[image_name])
        if image_file:  # //じゃなかった(ファイル名まである)
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

    # Canny
    for file_path in image_files:
        img = cv2.imread(file_path)
        minVal = int(max(0, (1.0 - 0.33) * 0.5))
        maxVal = int(max(255, (1.0 + 0.33) * 0.5))
        new_img = cv2.Canny(img, threshold1=minVal, threshold2=maxVal)

        # 出力先に保存
        output_file_path = os.path.join(output_dir, os.path.basename(file_path))
        cv2.imwrite(output_file_path, new_img)

    response.headers['Cache-Control'] = 'no-cache'
    return {'result':"Complete"}

run(app, host='localhost', port=8080, reloader=True)
