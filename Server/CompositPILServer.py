from bottle import Bottle, run, request, response
import re, os.path
import cv2

app = Bottle()

@app.route('/')
def hello():
    return "hello!"

@app.route('/canny')
def canny():
    print("---------------------------------")
    print(list(request.params.items()))

    output_path = request.params["output_path"]

    image_names = ["image_name1", "image_name2", "image_name3"]
    image_files = set([])  # 見つけたファイル記録場所
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

    print(output_path)
    print(image_files)

    # path = "C:/Users/jpibi/Desktop/test/tmp/"
    # files = ["sample-{:03d}.png".format(i+1) for i in range(24)]

    # for file in files:
    #     im = cv2.imread(path + file)
    #     minVal = int(max(0, (1.0 - 0.33) * 0.5))
    #     maxVal = int(max(255, (1.0 + 0.33) * 0.5))
    #     new_im = cv2.Canny(im, threshold1=minVal, threshold2=maxVal)

    #     cv2.imwrite(path + "compil" + file, new_im)

    response.headers['Cache-Control'] = 'no-cache'
    return {'result':"Complete"}

run(app, host='localhost', port=8080, reloader=True)
