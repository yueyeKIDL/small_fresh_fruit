from django.test import TestCase

from small_fresh_fruit.utils import check_tomato_bell


# Create your tests here.
class QuestionMethodTests(TestCase):

    def test_over_30_words_symbols(self):
        """
        超过30个字符数逗号
        """
        tomato_bell_reply = 'fqz 2 15 清华东区网红好的欠我一千万，都为技巧哦为绝地枪王为我就去玩为偶奇气温会丢失富瀚微，绯闻红为和非为违反为我覅偶还未发货未of维护'
        self.assertIs(check_tomato_bell(tomato_bell_reply), True)

    def test_over_30_words_space(self):
        """
        超过30个字符数空格
        """
        tomato_bell_reply = 'fqz 2 15 清华东区网红好的欠我一千万 都为技巧哦为绝地枪王为我就去玩为偶奇气温会丢失富瀚微  绯闻红为和我覅偶还未待确定未群多群发货未of维护'
        self.assertIs(check_tomato_bell(tomato_bell_reply), True)

    def test_ens_symbols(self):
        """英文逗号"""
        tomato_bell_reply = "fqz 2 15 Let's Go,here we go!"
        self.assertIs(check_tomato_bell(tomato_bell_reply), True)

    def test_ens_space(self):
        """英文空格"""
        tomato_bell_reply = "fqz 2 15 Let's Go here we go!"
        self.assertIs(check_tomato_bell(tomato_bell_reply), True)

    def test_return_correct_symbols(self):
        """
        测试返回内容是否一致逗号
        """
        tomato_bell_reply = 'fqz 2 15 清华东区网红好的欠我一千万，都为技巧哦为绝地枪王为我就去玩为偶奇气温会丢失富瀚微，绯闻红为和非为违反为我覅偶还未发货未of维护'
        t_, amount, minutes, *tomato_name = tomato_bell_reply.split()
        tomato_name = ' '.join(tomato_name)
        self.assertIs(tomato_name, '清华东区网红好的欠我一千万，都为技巧哦为绝地枪王为我就去玩为偶奇气温会丢失富瀚微，绯闻红为和非为违反为我覅偶还未发货未of维护')
    #
    # def test_return_correct_space(self):
    #     """
    #     测试返回内容是否一致空格
    #     """
    #     tomato_bell_reply = 'fqz 2 15 清华东区网红好的欠我一千万 都为技巧哦为绝地枪王为我就去玩为偶奇气温会丢失富瀚微  绯闻红为和我覅偶还未待确定未群多群发货未of维护'
    #     t_, amount, minutes, *tomato_name = tomato_bell_reply.split()
    #     tomato_name = ' '.join(tomato_name)
    #     self.assertIs(tomato_name, '清华东区网红好的欠我一千万 都为技巧哦为绝地枪王为我就去玩为偶奇气温会丢失富瀚微 绯闻红为和我覅偶还未待确定未群多群发货未of维护')

    def test_return_correct_ens_symbols(self):
        """
        测试返回内容是否一致英文逗号
        """
        tomato_bell_reply = "fqz 2 15 Let's Go,here we go!"
        t_, amount, minutes, *tomato_name = tomato_bell_reply.split()
        tomato_name = ' '.join(tomato_name)
        self.assertIs(tomato_name, "Let's Go,here we go!")

    def test_return_correct_ens_space(self):
        """
        测试返回内容是否一致英文空格
        """
        tomato_bell_reply = "fqz 2 15 Let's Go here we go!"
        t_, amount, minutes, *tomato_name = tomato_bell_reply.split()
        tomato_name = ' '.join(tomato_name)
        self.assertIs(tomato_name, "Let's Go here we go!")
