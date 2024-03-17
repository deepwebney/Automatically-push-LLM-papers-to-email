import arxiv
import os
import pickle
from fastlid import fastlid
import requests
from hashlib import md5
import random
import shutil
import base64


class ManagementPaper:
    def __init__(self, number=50, root_path='/data/zhangxiao/luoxuanpu/', push_num=5, trans=False) -> None:
        self.per_get_max_paper_num = number
        self.root_path = root_path
        self.push_num = push_num
        self.appid = '20240317001995807'
        self.appkey = 'Exdhqp4PPQgQqdep3RdS'
        self.trans = trans
        self.afterabstract = ''
        
    def _update_file(self, path, res_list):
        file_path = self.root_path + path
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                data = pickle.load(f)
            #备份剩余库
            source_file = file_path
            target_file = file_path[:-4] + '_copy.pkl'
            shutil.copy(source_file, target_file)
        else:
            data = {}

        # 爬虫备份
        pachong = []
        for item in res_list:
            per = {item.entry_id:{'date':item.published, 'title':item.title, 'abs':item.summary, 'pdf':item.pdf_url}}
            pachong.append(per)
            print(item.entry_id)
            if item.entry_id not in data:
                data.update(per)
        path_pa = file_path[:-4]+'_pachong.pkl'
        with open(path_pa, 'wb') as f:
            pickle.dump(pachong, f)
        
        num_to_take = min(self.push_num, len(data))
        sorted_items = sorted(data.items(), key=lambda x: x[1]['date'])
        taken_items = [sorted_items.pop(0) for _ in range(num_to_take)]
        sorted_items_dict = {key: value for key, value in sorted_items}
        with open(file_path, 'wb') as file:
            pickle.dump(sorted_items_dict, file)
        return taken_items

    
    def get_arxiv_paper(self, query_list, field):
        client = arxiv.Client()
        query_add = ['cat:' + i for i in query_list]
        query_field = '(' + ' OR '.join(query_add) + ')'
        paper = []
        for f in field:
            q = query_field + ' AND all:"{}"'.format(f)
            print(q)
            search = arxiv.Search(
            query = q,
            # '(cat:cs.CL OR cat:cs.AI OR cat:cs.LG) AND all:"LLM"'
            max_results = self.per_get_max_paper_num,
            sort_by = arxiv.SortCriterion.SubmittedDate,
            sort_order = arxiv.SortOrder.Descending
            )
            result = list(client.results(search))
            print(result)
            path = 'last_{}.pkl'.format(f)
            res = self._update_file(path, result)
            paper.extend([(x[0], {**x[1], 'field': f}) for x in res])
        print(paper)
        unique_dict = {}
        for item in paper:
            key = item[0]  # 假设以'id'作为唯一标识
            unique_dict[key] = item[1]

        # 去重后的结果
        unique_list = list(unique_dict.values())
        return unique_list
    
    def abs2trans(self, res_list):
        for idx, item in enumerate(res_list):
            abstract = self.translate(item['abs'])
            res_list[idx]['abs'] = abstract
        return res_list
    
    
    def generate_text(self, res_list):
        paper_dic = {}
        paper_list = []
                
        for item in res_list:
            if item['field'] not in paper_dic:
                paper_dic[item['field']] = [{'title':item['title'], 'abs':item['abs'], 'pdf':item['pdf']}]
            else:
                paper_dic[item['field']].append({'title':item['title'], 'abs':item['abs'], 'pdf':item['pdf']})
        for k, v in paper_dic.items():
            div = "{}\n".format(k)
            art_list = []
            for idx, art in enumerate(v):
                tmp = '{}. {}\n{}\n{}'.format(idx, art['title'], art['abs'], art['pdf'])
                art_list.append(tmp)
            div = div + '\n'.join(art_list)
            paper_list.append(div)
        return '\n'.join(paper_list)
    
    def generate_html(self, res_list):
        paper_dic = {}
        for item in res_list:
            if item['field'] not in paper_dic:
                paper_dic[item['field']] = [{'title':item['title'], 'abs':item['abs'], 'pdf':item['pdf']}]
            else:
                paper_dic[item['field']].append({'title':item['title'], 'abs':item['abs'], 'pdf':item['pdf']})
        div_lst = []
        for k, v in paper_dic.items():
            div = """\
                <div class="column">
                    <h2>{}</h2>
            """.format(k)
            art_list = []
            for idx, art in enumerate(v):
                template = """\
                    <div class="article">
                        <p><span>{}.</span> <span class="title">{}</span></p>
                        <p class="abstract">{}</p>
                        <p><a href="{}">阅读全文</a></p>
                    </div>
                """.format(idx+1, art['title'], art['abs'], art['pdf'])
                art_list.append(template)
            div = div + '\n'.join(art_list) + '\n</div>' 
            div_lst.append(div)
        with open('/data/zhangxiao/luoxuanpu/ads.jpg', "rb") as image_file:
            img = base64.b64encode(image_file.read()).decode('utf-8')
        html = """\
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>最新论文列表</title>
                <style>
                    .column {
                        float: left;
                        width: 100%;
                        padding: 10px;
                    }

                    .article {
                        margin-bottom: 20px;
                    }

                    .title {
                        font-weight: bold;
                        font-size: 1.2em;
                    }

                    .abstract {
                        font-size: 0.9em;
                    }
                </style>
            </head>
            <body>
        """ + '\n\n'.join(div_lst) + """\
        <div class="column">
        <p>github：https://github.com/deepwebney.</p>
        <p>小红书：不穿格子衫</p>
        <p><span style="font-size: 20px; font-weight: bold;">分享给你的朋友们，免费赠送一个月的订阅！！</span></p>
        <img src="data:./ads/jpg;base64,{}" alt="广告位！！欢迎打广子" style="width: 50%;">
        </div>  
            </body>
            </html>

        """.format(img)
        return html
    
    def _make_md5(self, s, encoding='utf-8'):
        return md5(s.encode(encoding)).hexdigest()
    
    def _baidu_api(self, query, from_lang, to_lang, url):
        salt = random.randint(32768, 65536)
        sign = self._make_md5(self.appid + query + str(salt) + self.appkey)

        # Build request
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        payload = {'appid': self.appid, 'q': query, 'from': from_lang, 'to': to_lang, 'salt': salt, 'sign': sign}

        # Send request
        r = requests.post(url, params=payload, headers=headers)
        result = r.json()

        # Show response
        #print(json.dumps(result, indent=4, ensure_ascii=False))
        return result["trans_result"][0]['dst']
    
    def translate(self, summary):
        summary = summary.strip().replace('\n', ' ')
        lang = fastlid(summary)
        if lang == "zh":
            from_lang, to_lang = "zh", "en"
        elif lang == "en":
            from_lang, to_lang = "en", "zh"
        else:
            from_lang = lang[0]
            to_lang = "zh"

        url = "https://fanyi-api.baidu.com/api/trans/vip/fieldtranslate"
        trans = self._baidu_api(summary, from_lang, to_lang, url)
        return trans
            
    

if __name__ == '__main__':
    a = ManagementPaper()
    t = a.translate('However, generation remains inefficient due to the need to store in memory a cache of key-value representations for past tokens, whose size scales linearly with the input sequence length and batch size. ')
    print(t)