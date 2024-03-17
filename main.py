# coding: utf-8
import arxiv
import os
import pickle
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from get_arxiv_paper import ManagementPaper
from send_email import send_email



if __name__ == '__main__':
    mange = ManagementPaper(number=30, push_num=5, trans=True)
    area = ['cs.CL', 'cs.AI', 'cs.LG']
    query = ['LLM', 'RLHF', 'RAG', 'CoT', 'PPO']
    # query = ['LLM']
    paper = mange.get_arxiv_paper(area, query)
    if mange.trans == True:
        paper = mange.abs2trans(paper)
    text = mange.generate_text(paper)
    html = mange.generate_html(paper)
    send_email([emil list], 'test', text, html)
    
