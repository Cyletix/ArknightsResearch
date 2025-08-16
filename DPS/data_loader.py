# data_loader.py
import requests
import json
import re
from urllib.parse import unquote
from bs4 import BeautifulSoup
from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtCore import pyqtSignal
import os


def log_to_file(filename, content):
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    try:
        with open(os.path.join(log_dir, filename), "w", encoding="utf-8") as f:
            f.write(content)
        print(f"日志已保存到: {os.path.join(log_dir, filename)}")
    except Exception as e:
        print(f"写入日志失败: {e}")


class DraggableTextEdit(QTextEdit):
    fileDropped = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            e.acceptProposedAction()
        else:
            e.ignore()

    def dragMoveEvent(self, e):
        if e.mimeData().hasUrls():
            e.acceptProposedAction()
        else:
            e.ignore()

    def dropEvent(self, e):
        if e.mimeData().hasUrls():
            url = e.mimeData().urls()[0]
            if url.isLocalFile() and url.toLocalFile().endswith(".html"):
                self.fileDropped.emit(url.toLocalFile())
        else:
            e.ignore()


class DataLoader:
    def __init__(self):
        self.API_URL = "https://m.prts.wiki/api.php"

    def _cargo_query(self, params):
        base_params = {"action": "cargoquery", "format": "json", "limit": 500}
        # [修改] 增加一个模拟浏览器的headers，防止被屏蔽
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        try:
            response = requests.get(
                self.API_URL, params={**base_params, **params}, timeout=10, headers=headers
            )
            response.raise_for_status()
            return response.json().get("cargoquery", [])
        except requests.exceptions.RequestException as e:
            print(f"Cargo query failed: {e}")
            return None

    def _fetch_page_html(self, page_name):
        params = {
            "action": "parse",
            "page": page_name,
            "prop": "text",
            "format": "json",
        }
        # [修改] 同样增加headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        try:
            response = requests.get(self.API_URL, params=params, timeout=10, headers=headers)
            response.raise_for_status()
            return response.json()["parse"]["text"]["*"]
        except (requests.exceptions.RequestException, KeyError) as e:
            print(f"从API获取HTML失败: {e}")
            return None

    def fetch_operator_data_from_html(self, operator_name):
        """[新的在线获取功能] 采用稳定的HTML获取和解析策略"""
        try:
            html_content = self._fetch_page_html(operator_name)
            if not html_content:
                return {"error": "网络请求失败：无法获取页面HTML内容"}
            log_to_file(f"log_{operator_name}_1_page.html", html_content)
            print("HTML获取成功，正在调用在线HTML解析器(parse_html_prts)...")
            parsed_data = self.parse_html_prts(html_content)
            return parsed_data
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {"error": f"处理在线数据时发生未知错误: {e}"}

    def _parse_html_for_fallback(self, html_content, data):
        soup = BeautifulSoup(html_content, "html.parser")
        trait_header = soup.find("span", id="特性")
        if trait_header:
            trait_table = (
                trait_header.find_parent("h2")
                .find_next_sibling("section")
                .find("table")
            )
            if trait_table and len(trait_table.select("td")) > 1:
                data["特性-描述"] = trait_table.select("td")[1].text.strip()

    def extract_name_from_input(self, user_input):
        if "prts.wiki" in user_input:
            try:
                return unquote(user_input.split("/")[-1])
            except:
                return user_input.strip()
        return user_input.strip()

    def parse_html(self, html_content):
        """[本地文件功能-最终修正版]"""
        soup = BeautifulSoup(html_content, "html.parser")
        data = {"attributes": {}, "trust_bonus": {}}
        try:
            name_tag = soup.find("div", class_="charname") or soup.find("h1", id="firstHeading")
            if name_tag:
                data["干员名称"] = name_tag.text.strip()
            else:
                raise ValueError("未能找到干员名称")
            class_tag = soup.select_one(".charclass-img img")
            if class_tag and class_tag.get("src"):
                src = class_tag.get("src")
                if "近卫" in src: data["职业"] = "近卫"
                elif "狙击" in src: data["职业"] = "狙击"
                elif "重装" in src: data["职业"] = "重装"
                elif "医疗" in src: data["职业"] = "医疗"
                elif "辅助" in src: data["职业"] = "辅助"
                elif "术师" in src: data["职业"] = "术师"
                elif "先锋" in src: data["职业"] = "先锋"
                elif "特种" in src: data["职业"] = "特种"
            else:
                script_tag = soup.find("script", string=re.compile(r"var char_info"))
                if script_tag:
                    match = re.search(r'"class"\s*:\s*"([^"]+)"', script_tag.string)
                    if match:
                        data["职业"] = match.group(1)
            rarity_img = soup.select_one(".charstar img")
            if rarity_img and rarity_img.get("src"):
                rarity_text = rarity_img["src"].split("_")[-1].split(".")[0]
                data["稀有度"] = int(rarity_text) if rarity_text.isdigit() else 6
            attr_header = soup.find("span", id="属性")
            if attr_header:
                parent_h2 = attr_header.find_parent("h2")
                extra_attr_table = parent_h2.find_next("table", class_="char-extra-attr-table")
                if extra_attr_table:
                    th_map = {}
                    for row in extra_attr_table.find_all("tr"):
                        ths = row.find_all('th')
                        tds = row.find_all('td')
                        if len(ths) == len(tds) and len(ths) > 0:
                            for i in range(len(ths)):
                                th_map[ths[i].text.strip()] = tds[i].text.strip()
                    data["再部署时间"] = th_map.get("再部署时间", "")
                    data["cost_progression"] = th_map.get("初始部署费用", "")
                    data["阻挡数"] = th_map.get("阻挡数", "")
                    data["攻击间隔"] = th_map.get("攻击间隔", "")
                attr_table = parent_h2.find_next("table", class_="char-base-attr-table")
                if attr_table:
                    rows = attr_table.find("tbody").find_all("tr")
                    key_map = {"生命上限": "hp", "攻击": "atk", "防御": "def", "法术抗性": "res"}
                    for row in rows[1:]:
                        cols = row.find_all("td")
                        attr_name_th = row.find("th")
                        if not cols or not attr_name_th: continue
                        attr_name = attr_name_th.text.strip()
                        if attr_name in key_map:
                            attr_key = key_map[attr_name]
                            data["attributes"][attr_key] = [c.text.strip() for c in cols[:-1] if c.text.strip()]
                            trust_val = cols[-1].text.strip()
                            if trust_val:
                                data["trust_bonus"][attr_key] = trust_val
            self._parse_html_for_fallback(html_content, data)
            talent_header = soup.find("span", id="天赋")
            if talent_header:
                data["天赋"] = []
                current_element = talent_header.find_parent("h2")
                for sibling in current_element.find_next_siblings():
                    if sibling.name == 'h2': break
                    tables_to_check = []
                    if sibling.name == 'section':
                        tables_to_check = sibling.find_all('table', class_='wikitable')
                    elif sibling.name == 'table' and 'wikitable' in sibling.get('class', []):
                        tables_to_check.append(sibling)
                    for table in tables_to_check:
                        for row in table.find_all("tr")[1:]:
                            cols = row.find_all("td")
                            if len(cols) >= 3 and "备注" not in row.text:
                                data["天赋"].append({"名称": cols[0].text.strip(), "条件": cols[1].text.strip(), "描述": " ".join(cols[2].text.strip().split())})
            potential_header = soup.find("span", id="潜能提升")
            if potential_header:
                data["潜能"] = []
                current_element = potential_header.find_parent("h2")
                search_area = current_element.find_next_sibling()
                if search_area:
                    potential_table = search_area if search_area.name == 'table' else search_area.find('table')
                    if potential_table:
                        for row in potential_table.find_all("tr"):
                            cols = row.find_all(["th", "td"])
                            if len(cols) == 2:
                                data["潜能"].append({"等级": cols[0].text.strip(), "描述": cols[1].text.strip()})
            skill_header = soup.find("span", id="技能")
            if skill_header:
                current_element = skill_header.find_parent("h2")
                skill_tables = []
                for sibling in current_element.find_next_siblings():
                    if sibling.name == 'h2': break
                    if sibling.name == 'section':
                        skill_tables.extend(sibling.find_all('table', class_='wikitable'))
                    elif sibling.name == 'table' and 'wikitable' in sibling.get('class', []):
                        skill_tables.append(sibling)
                for i, table in enumerate(skill_tables):
                    if i >= 3: break
                    skill_num = i + 1
                    skill_data = {}
                    header_row = table.find("tr")
                    if not header_row or not header_row.find("big"): continue
                    skill_data["名称"] = header_row.find("big").text.strip()
                    sp_info = header_row.text
                    skill_data["回复类型"] = ("受击回复" if "受击回复" in sp_info else "攻击回复" if "攻击回复" in sp_info else "自动回复")
                    skill_data["触发类型"] = ("自动触发" if "自动触发" in sp_info else "手动触发")
                    skill_levels = {}
                    for row in table.find_all("tr")[2:]:
                        cols = row.find_all(["th", "td"])
                        if len(cols) >= 5 and "备注" not in row.text:
                            level_text = cols[0].text.strip().replace("专精 ", "Rank ")
                            duration_text = cols[4].text.strip()
                            duration_match = re.search(r'[\d\.]+', duration_text)
                            duration_val = duration_match.group() if duration_match else "0"
                            skill_levels[level_text] = { "description": " ".join(cols[1].text.strip().split()), "initial_sp": cols[2].text.strip(), "sp_cost": cols[3].text.strip(), "duration": duration_val }
                    skill_data["levels"] = skill_levels
                    data[f"技能 {skill_num}"] = skill_data
            return data
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {"error": f"解析本地HTML文件时发生严重错误: {e}"}

    def parse_html_prts(self, html_content):
        """[在线解析最终修正版 V5]"""
        try:
            log_to_file("parser_input_content.html", html_content)
            soup = BeautifulSoup(html_content, "html.parser")
            data = {"attributes": {}, "trust_bonus": {}}
            name_tag = soup.select_one(".pathnav2-right") or \
                       soup.find("div", class_="charname") or \
                       soup.find("h1", id="firstHeading")
            if name_tag:
                data["干员名称"] = name_tag.text.strip()
            else:
                raise ValueError("未能找到干员名称")
            script_tag = soup.find("script", string=re.compile(r"var char_info"))
            if script_tag:
                rarity_match = re.search(r'"star"\s*:\s*(\d+)', script_tag.string)
                if rarity_match:
                    data["稀有度"] = int(rarity_match.group(1)) + 1
                class_match = re.search(r'"class"\s*:\s*"([^"]+)"', script_tag.string)
                if class_match:
                    data["职业"] = class_match.group(1)
            attr_header = soup.find("span", id="属性")
            if attr_header:
                parent_h2 = attr_header.find_parent("h2")
                section_container = parent_h2.find_next_sibling("section")
                if section_container:
                    extra_attr_table = section_container.find("table", class_="char-extra-attr-table")
                    if extra_attr_table:
                        th_map = {th.text.strip(): td.text.strip() for th, td in zip(extra_attr_table.find_all("th"), extra_attr_table.find_all("td"))}
                        data["再部署时间"] = th_map.get("再部署时间", "")
                        data["cost_progression"] = th_map.get("初始部署费用", "")
                        data["阻挡数"] = th_map.get("阻挡数", "")
                        data["攻击间隔"] = th_map.get("攻击间隔", "")
                    attr_table = section_container.find("table", class_="char-base-attr-table")
                    if attr_table:
                        rows = attr_table.find("tbody").find_all("tr")
                        key_map = {"生命上限": "hp", "攻击": "atk", "防御": "def", "法术抗性": "res"}
                        for row in rows[1:]:
                            cols = row.find_all("td")
                            attr_name_th = row.find("th")
                            if not cols or not attr_name_th: continue
                            attr_name = attr_name_th.text.strip()
                            if attr_name in key_map:
                                attr_key = key_map[attr_name]
                                attr_values = [c.text.strip() for c in cols[:-1]]
                                data["attributes"][attr_key] = attr_values
                                trust_val = cols[-1].text.strip()
                                if trust_val:
                                    data["trust_bonus"][attr_key] = trust_val
            self._parse_html_for_fallback(html_content, data)
            talent_header = soup.find("span", id="天赋")
            if talent_header:
                data["天赋"] = []
                current_element = talent_header.find_parent("h2")
                for sibling in current_element.find_next_siblings():
                    if sibling.name == 'h2': break
                    tables_to_check = []
                    if sibling.name == 'section':
                        tables_to_check = sibling.find_all('table', class_='wikitable')
                    elif sibling.name == 'table' and 'wikitable' in sibling.get('class', []):
                        tables_to_check.append(sibling)
                    for table in tables_to_check:
                        for row in table.find_all("tr")[1:]:
                            cols = row.find_all("td")
                            if len(cols) >= 3:
                                description_text = " ".join(cols[2].get_text(strip=True).split())
                                data["天赋"].append({"名称": cols[0].text.strip(), "条件": cols[1].text.strip(), "描述": description_text})
            potential_header = soup.find("span", id="潜能提升")
            if potential_header:
                data["潜能"] = []
                current_element = potential_header.find_parent("h2")
                search_area = current_element.find_next_sibling()
                if search_area:
                    potential_table = search_area if search_area.name == 'table' else search_area.find('table')
                    if potential_table:
                        for row in potential_table.find_all("tr"):
                            cols = row.find_all(["th", "td"])
                            if len(cols) == 2:
                                data["潜能"].append({"等级": cols[0].text.strip(), "描述": cols[1].text.strip()})
            skill_header = soup.find("span", id="技能")
            if skill_header:
                current_element = skill_header.find_parent("h2")
                skill_tables = []
                for sibling in current_element.find_next_siblings():
                    if sibling.name == 'h2': break
                    if sibling.name == 'section':
                        skill_tables.extend(sibling.find_all('table', class_='wikitable'))
                    elif sibling.name == 'table' and 'wikitable' in sibling.get('class', []):
                        skill_tables.append(sibling)
                for i, table in enumerate(skill_tables):
                    if i >= 3: break
                    skill_num = i + 1
                    header_row = table.find("tr")
                    if not header_row or not header_row.find("big"): continue
                    skill_data = {}
                    skill_data["名称"] = header_row.find("big").text.strip()
                    sp_info_tags = header_row.find_all("span", class_="mc-tooltips")
                    sp_info = " ".join(tag.text for tag in sp_info_tags)
                    skill_data["回复类型"] = ("受击回复" if "受击回复" in sp_info else "攻击回复" if "攻击回复" in sp_info else "自动回复")
                    skill_data["触发类型"] = ("自动触发" if "自动触发" in sp_info else "手动触发")
                    skill_levels = {}
                    for row in table.find_all("tr")[2:]:
                        cols = row.find_all(["th", "td"])
                        if len(cols) >= 5 and "备注" not in row.text:
                            level_text = cols[0].text.strip().replace("专精 ", "Rank ")
                            duration_text = cols[4].text.strip()
                            duration_match = re.search(r'[\d\.]+', duration_text)
                            duration_val = duration_match.group() if duration_match else "0"
                            if '无限' in duration_text: duration_val = "无限"
                            skill_levels[level_text] = {
                                "description": " ".join(cols[1].get_text(strip=True).split()),
                                "initial_sp": cols[2].text.strip(),
                                "sp_cost": cols[3].text.strip(),
                                "duration": duration_val
                            }
                    skill_data["levels"] = skill_levels
                    data[f"技能 {skill_num}"] = skill_data
            return data
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {"error": f"使用在线解析器(parse_html_prts)时发生错误: {e}"}