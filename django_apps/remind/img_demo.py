# -*- coding:utf-8 -*-
import random

from PIL import Image, ImageDraw, ImageFont

"""
【小鲜果儿<每日>提醒】
活泼的 "小鲜果儿"，您有一条提醒！
内容为：报饭
"""
solar_words = ['独树一帜', '戴月披星', '持之以恒', '斗志昂扬', '精诚团结', '见贤思齐', '自强不息', '不屈不挠', '别具匠心', '力争上游', '标新立异', '壮志凌云', '奋发图强',
               '坚持不懈', '坚定不移', '发奋图强', '百折不挠', '英勇无畏', '人定胜天', '一往无前', '知耻而后勇', '一日千里', '只争朝夕', '坚忍不拔', '朝气蓬勃', '铁杵成针',
               '百尺竿头', '锲而不舍', '苦心孤诣', '百尺竿头, 更进一步', '革故鼎新', '发愤忘食', '坚如磐石', '别具一格', '悬梁刺股', '坚持不懈', '革放鼎新', '水滴石穿',
               '不知寝食', '更进一步', '大智大勇', '不耻下问', '继往开来', '毛遂自荐', '积极进取', '矢志不移', '不甘示弱', '洗心革面', '奋不顾身', '坚毅顽强', '改天换地',
               '滴水穿石', '勇往直前', '推陈出新', '励精图治', '追根问底', '万象更新', '不甘后人', '囊萤映雪', '齐心协力', '精益求精', '兢兢业业']

# 话术
title = '<工作日>'
dear = '月夜小鲜果儿凑字数凑字数凑字数'
msg = '一条{}的提醒！'.format(random.choice(solar_words))
content = '月夜小鲜果儿凑字数技巧哦外交纠纷为为杰佛微积分辛苦破线情况我请客可千万都气我记得请我发情期觉得委屈'
print(len(content))

# 图片
img = r'../../media/reminder/base_img/timg.png'  # 图片模板
new_img = 'text.png'  # 生成的图片


# 字体
font_type = '../../media/reminder/fonts/small_fresh_fruit.TTF'
font = ImageFont.truetype(font_type, 28)
title_color = "red"
color = "#000000"

# 打开图片
image = Image.open(img)
draw = ImageDraw.Draw(image)
width, height = image.size

# 位置
title_x = 207
title_y = width - 198
title_line = 30

dear_x = 166
dear_y = width - 88
dear_line = 30

msg_x = 142
msg_y = width - 20
msg_line = 30

content_x1 = 163
content_y1 = width + 50

content_x2 = 78
content_y2 = width + 118

# 写入图片
# title
draw.text((title_x, title_y), '%s' % title, title_color, font)

# dear
if len(dear) > 8:
    dear = dear[:8] + '...'
draw.text((dear_x, dear_y), '%s' % dear, color, font)

# msg
draw.text((msg_x, msg_y), '%s' % msg, color, font)

# content
draw.text((content_x1, content_y1), '%s' % content[:10], color, font)
draw.text((content_x2, content_y2), '%s' % content[10:23], color, font)

# 生成图片
image.save(new_img, 'png')



# compress_img = 'compress.png'  # 压缩后的图片
# 压缩图片
# sImg = Image.open(new_img)
# w, h = sImg.size
# width = int(w / 2)
# height = int(h / 2)
# dImg = sImg.resize((width, height), Image.ANTIALIAS)
# dImg.save(compress_img)
