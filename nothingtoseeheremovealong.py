# -*- coding: utf-8 -*-
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from CMCLWidgets import *
from CMCLWidgets.Windows import RoundedDialogue
import time


def testtextof2233(parent=None, layout=None, attr_parent=None):
    if not parent:
        parent = QWidget()
        parent.show()
    layout = parent.layout() or QVBoxLayout(parent)
    if not attr_parent:
        attr_parent = parent
    print(parent, layout, parent.layout(), attr_parent)
    attr_parent.tip = Tip(parent, False)
    attr_parent.label = Label(attr_parent.tip)
    attr_parent.label.setText('''<a href="https://www.bilibili.com/v/topic/detail/?topic_id=53624&topic_name=2233%E7%94%9F%E6%97%A5%E5%BF%AB%E4%B9%90&spm_id_from=333.999.list.card_topic.click" style="text-decoration: none">#2233生日快乐#</a><br/>
                            (都说了全网带话题 <a href="https://www.bilibili.com/v/topic/detail/?topic_id=53624&topic_name=2233%E7%94%9F%E6%97%A5%E5%BF%AB%E4%B9%90&spm_id_from=333.999.list.card_topic.click" style="text-decoration: none">#2233生日快乐#</a>。这不，<small style="font-size: xx-small"><del style='text-decoration: line-through'>{}</del></small>的我也带了这个话题了。都别针对我呀，<small style="font-size: xx-small"><del style='text-decoration: line-through'>我是无辜的</del></small>。)'''.format(
        "远在地球另一边无法赶回来") if time.localtime().tm_mon == 8 and time.localtime().tm_mday == 16 else f"敬请等待{time.localtime().tm_year + 1}年8月16号<br/>{time.strftime('还有%M个月%d天', time.gmtime(time.mktime((time.gmtime().tm_year + 1, 9, 16, 19, 30, 0, 0, 0, 0)) - time.time()))}")
    # 2024: 远在地球另一边无法赶回来
    attr_parent.tip.setCentralWidget(attr_parent.label)
    
    def updateTime(label):
        year = time.localtime().tm_year if time.localtime().tm_mon < 8 or (
                time.localtime().tm_mon == 8 and time.localtime().tm_mday < 16) else (
                time.localtime().tm_year + 1)
        time_s = time.gmtime(time.mktime((year, 8, 16, 0, 0, 0, 0, 0, 0)) - time.time())
        time_text = f"还有{time_s.tm_mon - 1}个月{time_s.tm_mday}天"
        wait_text = f"敬请等待{year}年8月16号<br/>{time_text}"
        topic_text = f'<a href="{"https://www.bilibili.com/v/topic/detail/?topic_id=53624"}" style="text-decoration: none">#{"2233生日快乐"}#</a><br/>(都说了全网带话题 <a href="{"https://www.bilibili.com/v/topic/detail/?topic_id=53624"}" style="text-decoration: none">#{"2233生日快乐"}#</a>。这不，<small style="font-size: xx-small"><del style="text-decoration: line-through">{"远在地球另一边无法赶回来"}</del></small>的我也带了这个话题了。都别针对我呀，<small style="font-size: xx-small"><del style="text-decoration: line-through">我是无辜的</del></small>。)'
        label.setText(
            topic_text if time.localtime().tm_mon == 8 and time.localtime().tm_mday == 16 else wait_text)
    
    t = QTimer(parent)
    t.timeout.connect(lambda: updateTime(attr_parent.label))
    t.start(1000)
    layout.addWidget(attr_parent.tip)
    attr_parent.label2 = Label(parent)
    attr_parent.label2.setText((f"""<!DOCTYPE html>
                                <html>
                                    <head/>
                                    <body>
                                        <p>
                                        <hr/>
                                        <h2>开头</h2>
                                        ---------<br/>
                                        你知道 Bilibili 的站娘 22 和 33 吗？<br/>
                                        <small style="font-size: xx-small"><del style='text-decoration: line-through'>我知道你不知道她们</del></small>(bushi)<br/>
                                        22 和 33: 给你一次重新组织语言的机会，你知不知道我们？<br/>
                                        <small style="font-size: xx-small"><del style='text-decoration: line-through'>她们的生日在8月多少号来着？？？</del></small><br/>
                                        22 和 33: 你号没了！去小黑屋罚抄“2233生日在8月16号*100遍”！！！<br/>
                                        由此可得知她们都是狮子座。<br/>
                                        ---------<br/>
                                        上面的纯粹是在娱乐<br/>
                                        <a href='https://space.bilibili.com/68559'>这里是她们的官方账号(https://space.bilibili.com/68559)</a><br/>
                                        当然，设定也要讲的了。<br/>
                                        <h2>设定</h2>
                                        ---------<br/>
                                        让我们先说 22 吧 <br/>
                                        <h3>22 的设定</h3>
                                        身高：160cm <br/>
                                        体重：48KG<br/>
                                        生日：8月16日<br/>
                                        <small style="font-size: xx-small"><del style='text-decoration: line-through'>绰号：F22<br/>想知道更多可以去<a href="https://www.bilibili.com/video/BV1wJ411J7JK/">https://www.bilibili.com/video/BV1wJ411J7JK/</a>一探究竟。</del></small><br/>
                                        声优：
                                        <ul>
                                            <li style="display: list-item;">柴刀娘木木（2015）</li>
                                            <li style="display: list-item;">幽舞越山（2016--）</li>
                                            <li style="display: list-item;"><del style='text-decoration: line-through'>AI（2024年唱歌）</del><li/>
                                        </ul>
                                        <br/>
                                        再来说 33 吧 <br/>
                                        <h3>33 的设定</h3>
                                        身高：148cm <br/>
                                        体重：？？？（怕 33 咬我，可以告诉你们 2 开头）<br/>
                                        生日：8月16日<br/>
                                        声优：
                                        <ul>
                                            <li style="display: list-item;">柴刀娘木木（2015）</li>
                                            <li style="display: list-item;">少愿愿（2016-2018）</li>
                                            <li style="display: list-item;">李姗姗（2019--）</li>
                                            <li style="display: list-item;">Hanser（部分歌曲？）</li>
                                            <li style="display: list-item;"><del style='text-decoration: line-through'>AI（2024年唱歌）</del></li>
                                        </ul>
                                        <br/>
                                        <h2>概述</h2>
                                        ---------<br/>
                                        22娘为姐姐，33娘为妹妹，于2010年8月16日由Bilibili站娘投票结果产生。<br/>
                                        <h2>属性</h2>
                                        ---------<br/>
                                        <h3>22娘的属性</h3>
                                        <ul>
                                            <li style="display: list-item;">姐姐是个阳光元气娘，非常活泼有精神，对人热情，热心帮忙。但有些冒冒失失。</li>
                                            <li style="display: list-item;">偶尔还会心血来潮做点发明改造，有时改进下播放器等等，<small style="font-size: xx-small"><del style='text-decoration: line-through'>但是她做出来东西经常是会有BUG的，往往需要妹妹二次修复，而且因为姐姐的冒失，妹妹经常腹黑的吐槽。<br/>(感兴趣的，可以去 <a href="https://mzh.moegirl.org.cn/File:%E8%A6%81%E5%B8%AE%E5%BF%99%E5%90%97.jpg">https://mzh.moegirl.org.cn/File:%E8%A6%81%E5%B8%AE%E5%BF%99%E5%90%97.jpg</a> 看一下)</del></small><br/>(仅供娱乐，请勿当真)</li>
                                            <li style="display: list-item;">姐姐充满干劲，而且这种表现常常会感染到周遭的人，妹妹最喜欢姐姐这点了。</li>
                                            <li style="display: list-item;">性格上很乐观，<small style="font-size: xx-small"><del style='text-decoration: line-through'>但也会因某些事儿消极</del></small>(就当刚才那句我胡说)，偶尔傲娇一下，比较喜欢跟妹妹傲娇。</li>
                                            <li style="display: list-item;"><small style="font-size: xx-small"><del style='text-decoration: line-through'>姐姐很害怕猎奇、恐怖类事物，每每审核到这类型视频，都会被吓哭，结果这部分视频都是交由妹妹帮忙审核。</del></small>(这条我编的，都别信，我号还要)</li>
                                            <li style="display: list-item;">毕竟是姐姐，常常有保护妹妹的欲望，<small style="font-size: xx-small"><del style='text-decoration: line-through'>但往往需要被保护的都是自己。</del></small>(刚才那句我瞎说)</li>
                                        </ul>
                                        <br/>
                                        <h3>33娘的属性</h3>
                                        <ul>
                                            <li style="display: list-item;">妹妹是个机娘，个性沉默寡言，情感冷静少起伏且表情缺乏变化。</li>
                                            <li style="display: list-item;">别看是妹妹，平时都是她来给网站维护服务器和鼓弄网站各种程序。有着惊人的知识量，记忆力。<small style="font-size: xx-small"><del style='text-decoration: line-through'>(chengwm（CMCL启动器作者）： 33，请问我能......)</del></small></li>
                                            <li style="display: list-item;">爱发明和创造物品，<small style="font-size: xx-small"><del style='text-decoration: line-through'>但大多数都是奇奇怪怪的，就比如<a href="https://mzh.moegirl.org.cn/File:%E5%A5%87%E5%A5%87%E6%80%AA%E6%80%AA.jpg">https://mzh.moegirl.org.cn/File:%E5%A5%87%E5%A5%87%E6%80%AA%E6%80%AA.jpg</a>这张图片。</del></small>(仅供娱乐，请勿当真)</li>
                                            <li style="display: list-item;">妹妹需要充电，在身后（臀部）插入插头形状的“尾巴”，连上插座即可充电,当然也可以吃电池来充电。<del style='text-decoration: line-through'>(难道这就是呆毛事故的原因吗？)</del></li>
                                            <li style="display: list-item;">妹妹有两个怪癖，一是平时没事喜欢啃插座<del style='text-decoration: line-through'>(22: 啊疼疼疼疼疼)</del>；二是虽说是个机娘，但是睡觉的时候不抱着东西，就无法入睡。</li>
                                            <li style="display: list-item;">妹妹虽然经常会因为姐姐的冒失而吐槽，但是心里还是很十分喜欢姐姐的。妹妹虽然经常会因为姐姐的冒失而吐槽，但是心里还是很十分喜欢姐姐的。</li>
                                            <li style="display: list-item;">据说33不会被蚊子咬？</li>
                                        </ul>
                                        <br/>
                                        <h2>目前为止可以公开(或者不会被封号)的情报</h2>
                                        ---------<br/>
                                        <ul>
                                            <li style="display: list-item;">22的腰包有好几种，四次元腰包可以装的下任何东西（类似于哆啦A梦的口袋）。(见<a href="https://mzh.moegirl.org.cn/File:22%E7%9A%84%E8%85%B0%E5%8C%85.jpg">https://mzh.moegirl.org.cn/File:22%E7%9A%84%E8%85%B0%E5%8C%85.jpg</a>)</li>
                                            <li style="display: list-item;">22身高160cm，33身高146cm，这个身高极其萌。(见<a href="https://mzh.moegirl.org.cn/File:2233%E8%BA%AB%E9%AB%98%E5%B7%AE.jpg">https://mzh.moegirl.org.cn/File:2233%E8%BA%AB%E9%AB%98%E5%B7%AE.jpg</a>)</li>
                                            <li style="display: list-item;">两位都有呆毛，貌似可当天线使用，但没有验证过。</li>
                                            <li style="display: list-item;">22娘是闪电型呆毛，33是月牙形呆毛，因为“bilibili”一名的来源为“电击使”御坂美琴，于是22的呆毛形状被设计成与电相关(见<a href="https://mzh.moegirl.org.cn/File:2233%E5%91%86%E6%AF%9B.jpg">https://mzh.moegirl.org.cn/File:2233%E5%91%86%E6%AF%9B.jpg</a>)</li>
                                            <li style="display: list-item;">两姐妹头发上都夹着个一样的小电视发夹（有时在左边有时在右边，并不是一般的发夹，小电视发夹上的表情是与2233同步变化）。(见<a href="https://mzh.moegirl.org.cn/File:%E5%8F%91%E5%A4%B9%E7%9A%84%E7%A7%98%E5%AF%86.jpg">https://mzh.moegirl.org.cn/File:%E5%8F%91%E5%A4%B9%E7%9A%84%E7%A7%98%E5%AF%86.jpg</a>)</li>
                                            <li style="display: list-item;">有时候33娘没有小电视发夹，只有播放按钮发夹，而且发夹自称是精灵球。(见<a href="https://mzh.moegirl.org.cn/File:%E7%B2%BE%E7%81%B5%E7%90%83%E5%8F%91%E5%A4%B9.jpg">https://mzh.moegirl.org.cn/File:%E7%B2%BE%E7%81%B5%E7%90%83%E5%8F%91%E5%A4%B9.jpg</a>)</li>
                                            <li style="display: list-item;">33在工作时喜欢穿白大褂，额头上有投影装置，还可以扫描解析，使用AR眼镜或额头上的投影装置都可以让33浮现操作面板，以更改自身设置以及浏览互联网等操作。(见<a href="https://mzh.moegirl.org.cn/File:%E5%85%B3%E4%BA%8E33%E5%A8%98.jpg">https://mzh.moegirl.org.cn/File:%E5%85%B3%E4%BA%8E33%E5%A8%98.jpg</a>)</li>
                                            <li style="display: list-item;">两姐妹都是ACG爱好者，也会追新番，也喜欢看各种神技术搞笑带弹幕吐槽的视频。（两人审核时，偶尔会被特别喜好的视频吸引住眼球，而忘记正在审核……）</li>
                                            <li style="display: list-item;">两姐妹都会审核视频，姐姐对着宠物小电视审核；妹妹则是从自己额头的成像仪投影出视频来审核。由于，网站视频的投稿量大，两人常常忙得不亦乐乎。其他方面，网站服务器维护以及各种程序基本都是由妹妹来完成，姐姐则多处理各种BILI众的意见或BUG的反馈。(PS：根据B站视频<a href="https://mzh.moegirl.org.cn/%E5%B9%B8%E7%A6%8F%E5%B0%B1%E5%9C%A8%E4%BD%A0%E8%BA%AB%E8%BE%B9">《Bilibili耶》</a>中，可以看出妹妹略带攻属性。)</li>
                                            <li style="display: list-item;">33左臂装有能量炮，可以向任意物体发射。(见<a href="https://mzh.moegirl.org.cn/File:Bilibili%E6%BC%AB%E7%94%BB%E5%AE%B3%E6%80%95.webp">https://mzh.moegirl.org.cn/File:Bilibili%E6%BC%AB%E7%94%BB%E5%AE%B3%E6%80%95.webp</a>)</li>
                                            <li style="display: list-item;">据说33的右臂是爱心飞拳？可以分离？还可以抓住物体？(见<a href="https://manga.bilibili.com/mc28173/455648">https://manga.bilibili.com/mc28173/455648</a>)</li>
                                        </ul>
                                        <br/>
                                        <h2>趣闻</h2>
                                        ---------<br/>
                                        <ul>
                                            <li style="display: list-item;"><small style="font-size: xx-small"><del style='text-decoration: line-through'>22有一次审核恐怖视频时被吓到了，晚上不敢去洗手间，结果第二天一早醒来发现自己尿床了(⊙o⊙)。结果晒床单时被妹妹33娘看见……</del></small>(都懂的......)</li>
                                            <li style="display: list-item;"><small style="font-size: xx-small"><del style='text-decoration: line-through'>22近期迷上了哲♂学、兄♂贵、摔♂跤以及FA♂乐器，用33的手机看了之后留下了喜好推荐被33发现，结果亲身体♂验了一番。(见<a href="https://mzh.moegirl.org.cn/File:%E4%BA%B2%E8%BA%AB%E4%BD%93%E9%AA%8C.jpg">https://mzh.moegirl.org.cn/File:%E4%BA%B2%E8%BA%AB%E4%BD%93%E9%AA%8C.jpg</a>)</del></small>(仅供娱乐)</li>
                                            <li style="display: list-item;"><small style="font-size: xx-small"><del style='text-decoration: line-through'>万圣节时22穿上十分可怕（十分可爱）的南瓜头进行万圣节传统活动去吓唬33讨糖，结果被踢了出来。(见<a href="https://mzh.moegirl.org.cn/File:%E4%B8%87%E5%9C%A3%E8%8A%82%E6%83%8A%E9%AD%82.jpg">https://mzh.moegirl.org.cn/File:%E4%B8%87%E5%9C%A3%E8%8A%82%E6%83%8A%E9%AD%82.jpg</a>)</del></small></li>
                                        </ul>
                                        <br/>
                                        <h2>一些不好说的东西</h2>
                                        ---------<br/>
                                        <small style="font-size: xx-small"><del style='text-decoration: line-through'>热知识：在2017年，2233 以 98 亿（9876547210.33元）被卖身。（雾）</del></small><br/>
                                        <small style="font-size: xx-small"><del style='text-decoration: line-through'>震惊，Bilibili的98亿竟被两个员工花完。（2021年拜年纪）</del></small>
                                      </p>
                                      <p>更多信息请前往<a href="https://mzh.moegirl.org.cn/Bilibili%E5%A8%98">此处</a>了解。<br/>
                                        ———— 2024年9月17日写于小黑屋<br/>
                                      </p>
                                      <h2>版权声明</h2>
                                      <p>---------</p>
                                      <p>
                                        此文本为CMCL启动器测试文本，为CMCL启动器测试文本显示、HTML样式测试、模板填空测试以及排版测试文本，不具有任何意义。著作权归原编辑者所有。<br/>
                                        还有，很多地方我瞎说的，别信！<br/>
                                      </p>
                                      <p>此文本介绍部分内容及数据引自萌娘百科(mzh.moegirl.org.cn)，具体链接：<a href="https://mzh.moegirl.org.cn/Bilibili%E5%A8%98">*</a>，<strong>内容不可商用，著作权归原编辑者所有</strong></p>
                                    </body>
                                </html>""" if time.localtime().tm_year != 2017 or time.localtime().tm_mon != 1 or time.localtime().tm_mday != 23 else "没有 98 亿还想知道 2233？") if time.localtime().tm_year > 2010 or (
            time.localtime().tm_year == 2010 and time.localtime().tm_mon > 8 or (
            time.localtime().tm_mon == 8 and time.localtime().tm_mday >= 16)) else "此条目不存在")
    attr_parent.label2.setTextInteractionFlags(
        Qt.TextInteractionFlag.TextSelectableByKeyboard | Qt.TextInteractionFlag.TextSelectableByMouse)  # | Qt.TextInteractionFlag.TextEditable)
    attr_parent.label2.setWordWrap(True)
    layout.addWidget(attr_parent.label2)


class TextDialogueBase(RoundedDialogue):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(8, 40, 8, 8)
        self.label = Label(self)
        self.layout.addWidget(self.label)
    
    def paintEvent(self, a0, **kwargs):
        painter = QPainter(self)
        painter.fillRect(
            QRect(-self.geometry().x(), -self.geometry().y(), QGuiApplication.primaryScreen().geometry().width(),
                  QGuiApplication.primaryScreen().geometry().height()),
            QGradient(QGradient.Preset.DeepBlue if getTheme() == Theme.Light else QGradient.Preset.PerfectBlue))


def let2233banyou1():
    class Let2233BanYouDialogue1(TextDialogueBase):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.label.setText(
                '“圆”这个字最适合用来形容2020年6月的2233啦！\n(请勿截图谢谢)\n(你要截图我也保不了你，我先保住我的号吧！)')
    
    dialogue = Let2233BanYouDialogue1()
    dialogue.exec()


def let2233banyou2():
    class Let2233BanYouDialogue2(TextDialogueBase):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.label.setText(
                'F22战斗姬！F22隐身战斗姬！\n(请勿截图谢谢)\n(你要截图我也保不了你，我先保住我的号吧！)')
    
    dialogue = Let2233BanYouDialogue2()
    dialogue.exec()
