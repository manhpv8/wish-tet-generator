import random
from loguru import logger
import configs
from controllers.search import GPTSearcher
from utils.text import get_text_topk, pharaphase_result, post_processing
from utils.common import listComplementElements


def generate_expection(exp_vocab,  expections, anomalous_level = False):
    r_expection = ""
    _expections = []

    if anomalous_level:
        post_sentence= "<LINKING_WORD> <OWN_LEVEL> chúc <LEVEL_1>"
    else:
        post_sentence= "<LINKING_WORD> <OWN_LEVEL> chúc <NAME>"
    
    for expection in expections:
        expection_results = get_text_topk(expection, exp_vocab, 3)
        expection_results = listComplementElements(expection_results, _expections)
        _expections.extend([random.sample(expection_results, 1)[-1][0]])
    
    if _expections == [] or len(_expections) < 3:
        _expections.extend(random.sample(exp_vocab, 3 - len(_expections)))

    unique_expections = list(set(_expections))
    r_expection = ", ".join(unique_expections[:-1])
    r_expection += " và " + unique_expections[-1]
    r_expection += f". {post_sentence} " + random.sample(configs.SPECIAL_EXPECTIONS_DEFAULT, 1)[-1]
    return r_expection


def generate_expection_1(exp_vocab,  expections, anomalous_level = False):
    r_expection = ""
    _expections = expections
    if _expections == [] or len(_expections) < 3:
        _expections.extend(random.sample(exp_vocab, 3 - len(_expections)))

    unique_expections = list(set(_expections))
    r_expection = ", ".join(unique_expections[:-1])
    r_expection += " và " + unique_expections[-1]
    return r_expection

    

def generate_backup(name, level, expections):
   
    pre_sentence = ["Tết đến xuân về, ", "2023 đã đến, ", "Nhân dịp đầu xuân, ", "Đầu xuân năm mới, ", "Năm mới đến rồi, ", "Nhân dịp đầu năm mới, ", "Đầu năm, ", "Đầu xuân, ", "Nhân dịp đầu xuân năm mới, ", "Nhân dịp Tết đến xuân sang, "]
    result = ""
    vocab = []
    wish_tet_list = []
    try:
        if level == 'bạn':
            wish_tet_list = configs.FRIEND_BACKUP_LIST
        
        elif level in ['anh', 'chị']:
            name = f"{level} {name}"
            wish_tet_list = configs.ANH_CHI_BACKUP_LIST

        elif level in ['cô', 'dì', 'chú', 'bác','thím', 'mợ' , 'cậu']:
            name = f"{level} {name}"
            wish_tet_list =  configs.COCHU_BACKUP_LIST   

        elif level in ['bố', 'mẹ']:
            wish_tet_list =  configs.BO_ME_BACKUP_LIST
            name = level
            if level == 'bố':
                vocab = [
                "ngày càng phong độ hơn",
                "làm ăn phát tài hơn",
                "kiếm được thật nhiều tiền"
                ]
            else:
                vocab = [
                "hạnh phúc ngập tràn",
                "tươi trẻ hơn",
                "ngày càng khỏe mạnh hơn",
                "luôn luôn tươi trẻ",
                "hạnh phúc bên bố và các con"
                ]
       
        r_expection = generate_expection(expections = expections, exp_vocab= configs.EXPECTIONS_DEFAULT + vocab)
        wish_tet_list = random.choice(wish_tet_list)
        wish_tet_result = f"{random.sample(pre_sentence, 1)[-1]} {wish_tet_list}"

    
        
    except Exception as e:
        logger.error(e)
        r_expection = generate_expection(
            expections = expections,
            exp_vocab= configs.EXPECTIONS_DEFAULT + vocab,
            anomalous_level = True)
        wish_tet_list = random.choice(configs.BACKUP_LIST)
        wish_tet_result = f"{random.sample(pre_sentence, 1)[-1]} {wish_tet_list}"
    
    wish_tet_result = wish_tet_result.replace("<EXPECT>", r_expection)

    return wish_tet_result


class TetWishGenerator:
    
    def __init__(self, config, timeout = 30):
        self.config = config
        self.searcher = None
        self.set_up(config=config)
        
        
    def set_up(self, config):
        self.searcher = GPTSearcher(
            config = config, 
            )
        
        
    def _generate_query(self, name,level,  expections):
        ex_context = generate_expection_1(expections = expections, exp_vocab = configs.EXPECTIONS_DEFAULT)
        generated_query = f"Tạo lời chúc Tết 2023 tới {name}, trong năm mới {level} {name} rất mong muốn {ex_context}"
        logger.info(f"Generated query: {generated_query} ") 
        return generated_query

    def generate(self, name = "", level = 'bạn', expections = []):
        result  = "Chúc mừng năm mới 2023!"
        try:
            pre_sentence = ["Tết đến xuân về, ", "2023 đã đến, ", "Nhân dịp đầu xuân, ", "Đầu xuân năm mới, ", "Năm mới đến rồi, ", "Nhân dịp đầu năm mới, ", "Đầu năm, ", "Đầu xuân, ", "Nhân dịp đầu xuân năm mới, ", "Nhân dịp Tết đến xuân sang, "]
            question_query = self._generate_query(name, level, expections)
            result = self.searcher.search(query_text = question_query)
            result = f"{random.sample(pre_sentence, 1)[-1]} {result}"

            post_sentence= "<LINKING_WORD> <OWN_LEVEL> chúc <LEVEL>"
            result += f". {post_sentence} " + random.sample(configs.SPECIAL_EXPECTIONS_DEFAULT, 1)[-1]

            for b_t in ["Thiên Chúa", "Chúa", "bổ ích"]:
                if b_t in result:
                    result = generate_backup(name, level, expections)
        except Exception as e:
            logger.error(e)
            result = generate_backup(name, level, expections)
        

        pharaphased_result = pharaphase_result(result, name, level)
        result = post_processing(pharaphased_result)
        return result