# data_loader.py (恢复了本地解析功能的最终完整版)
import requests
import json
import re
from urllib.parse import unquote
from bs4 import BeautifulSoup
from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtCore import pyqtSignal
import os


def log_to_file(filename, content):
    """一个简单的日志记录函数，现在会记录所有关键步骤"""
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
        try:
            response = requests.get(
                self.API_URL, params={**base_params, **params}, timeout=10
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
        try:
            response = requests.get(self.API_URL, params=params, timeout=10)
            response.raise_for_status()
            return response.json()["parse"]["text"]["*"]
        except (requests.exceptions.RequestException, KeyError) as e:
            print(f"从API获取HTML失败: {e}")
            return None

    def fetch_operator_data(self, operator_name):
        """[在线获取功能] 采用先获取charId再查询Cargo的稳健策略"""
        try:
            # 第1步：获取页面HTML
            html_content = self._fetch_page_html(operator_name)
            if not html_content:
                return {"error": "网络请求失败：无法获取页面HTML内容"}
            log_to_file(f"log_{operator_name}_1_page.html", html_content)

            # 第2步：从HTML中解析出charId
            soup = BeautifulSoup(html_content, "html.parser")
            spine_div = soup.find("div", id="spine-root")
            if not spine_div or "data-id" not in spine_div.attrs:
                return {"error": "解析失败：无法在页面中找到干员内部ID(charId)"}
            char_id = spine_div["data-id"]
            print(f"成功找到 {operator_name} 的 charId: {char_id}")

            # 第3步：使用charId进行精确的cargo查询
            op_data_list = self._cargo_query(
                {
                    "tables": "Operators",
                    "fields": "name, rarity, class, subClass, position, block, attackInterval, cost, cost_e1, cost_e2, redeploy, hp_i0_1, hp_i0_max, hp_i1_max, hp_i2_max, atk_i0_1, atk_i0_max, atk_i1_max, atk_i2_max, def_i0_1, def_i0_max, def_i1_max, def_i2_max, res_i0_1, res_i0_max, res_i1_max, res_i2_max, trustHp, trustAtk, trustDef",
                    "where": f"charId='{char_id}'",
                }
            )

            if not op_data_list:
                return {
                    "error": f"通过ID '{char_id}' 查询Cargo失败，请检查干员名称或网络"
                }

            log_to_file(
                f"log_{operator_name}_2_cargo_base.json",
                json.dumps(op_data_list, indent=2, ensure_ascii=False),
            )
            op_base = op_data_list[0]["title"]

            data = {
                "干员名称": op_base["name"],
                "稀有度": int(op_base["rarity"]) + 1,
                "职业": op_base["class"],
                "子职业": op_base["subClass"],
                "攻击间隔": f"{op_base['attackInterval']}s",
                "阻挡数": op_base["block"],
                "cost_progression": f"{op_base['cost']}→{op_base['cost_e1']}→{op_base.get('cost_e2', op_base['cost_e1'])}",
                "再部署时间": f"{op_base['redeploy']}s",
                "attributes": {
                    "hp": [
                        op_base["hp_i0_1"],
                        op_base["hp_i0_max"],
                        op_base["hp_i1_max"],
                        op_base["hp_i2_max"],
                    ],
                    "atk": [
                        op_base["atk_i0_1"],
                        op_base["atk_i0_max"],
                        op_base["atk_i1_max"],
                        op_base["atk_i2_max"],
                    ],
                    "def": [
                        op_base["def_i0_1"],
                        op_base["def_i0_max"],
                        op_base["def_i1_max"],
                        op_base["def_i2_max"],
                    ],
                    "res": [
                        op_base["res_i0_1"],
                        op_base["res_i0_max"],
                        op_base["res_i1_max"],
                        op_base["res_i2_max"],
                    ],
                },
                "trust_bonus": {
                    "hp": op_base.get("trustHp", "0"),
                    "atk": op_base.get("trustAtk", "0"),
                    "def": op_base.get("trustDef", "0"),
                },
            }

            potential_data = self._cargo_query(
                {
                    "tables": "Potentials",
                    "fields": "level, description",
                    "where": f"charId='{char_id}'",
                    "order_by": "level",
                }
            )
            data["潜能"] = [
                {
                    "等级": f"潜能{p['title']['level']}",
                    "描述": p["title"]["description"],
                }
                for p in potential_data
            ]

            talent_data = self._cargo_query(
                {
                    "tables": "Talents",
                    "fields": "talentName, unlock, description",
                    "where": f"charId='{char_id}'",
                }
            )
            data["天赋"] = [
                {
                    "名称": t["title"]["talentName"],
                    "条件": t["title"]["unlock"],
                    "描述": t["title"]["description"],
                }
                for t in talent_data
            ]

            skill_data_raw = self._cargo_query(
                {
                    "tables": "Skills",
                    "fields": "skillName, skillIndex, spType, trigger, levels",
                    "where": f"charId='{char_id}'",
                    "order_by": "skillIndex",
                }
            )
            log_to_file(
                f"log_{operator_name}_3_cargo_skills.json",
                json.dumps(skill_data_raw, indent=2, ensure_ascii=False),
            )

            for i, skill in enumerate(skill_data_raw):
                skill_info = skill["title"]
                levels_str = skill_info.get("levels", "[]")
                if not levels_str:
                    continue
                levels_data = json.loads(levels_str)
                level_map = {}
                for item in levels_data:
                    key = item["level"].replace("专精 ", "Rank ")
                    level_map[key] = {
                        "description": item.get("description", ""),
                        "sp_cost": item.get("spCost", ""),
                        "initial_sp": item.get("initialSp", ""),
                        "duration": item.get("duration", ""),
                        **item.get("variables", {}),
                    }
                data[f"技能{i+1}"] = {
                    "名称": skill_info["skillName"],
                    "回复类型": skill_info["spType"],
                    "触发类型": skill_info["trigger"],
                    "levels": level_map,
                }

            self._parse_html_for_fallback(html_content, data)
            log_to_file(
                f"log_{operator_name}_4_final_data.json",
                json.dumps(data, indent=2, ensure_ascii=False),
            )
            return data

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

# data_loader.py -> 请用此函数完整替换旧的 parse_html 函数

    def parse_html(self, html_content):
        """[本地文件功能-最终修正版]
        此函数专门用于解析您手动保存的、结构完整的HTML文件。
        """
        soup = BeautifulSoup(html_content, "html.parser")
        data = {"attributes": {}, "trust_bonus": {}}
        try:
            # [兼容修改] 兼容移动版和桌面版的干员名称获取
            name_tag = soup.find("div", class_="charname") or soup.find("h1", id="firstHeading")
            if name_tag:
                data["干员名称"] = name_tag.text.strip()
            else:
                raise ValueError("未能找到干员名称")

            # [新增] 兼容移动版和桌面版的职业获取
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

            # [最终兼容性修正] 以下是针对天赋、潜能、技能的最终修正逻辑
            
            # --- 天赋解析 ---
            talent_header = soup.find("span", id="天赋")
            if talent_header:
                data["天赋"] = []
                current_element = talent_header.find_parent("h2")
                for sibling in current_element.find_next_siblings():
                    if sibling.name == 'h2': break
                    tables_to_check = []
                    if sibling.name == 'section': # 移动版：在section内部查找
                        tables_to_check = sibling.find_all('table', class_='wikitable')
                    elif sibling.name == 'table' and 'wikitable' in sibling.get('class', []): # 桌面版：本身就是table
                        tables_to_check.append(sibling)
                    
                    for table in tables_to_check:
                        for row in table.find_all("tr")[1:]:
                            cols = row.find_all("td")
                            if len(cols) >= 3 and "备注" not in row.text:
                                data["天赋"].append({"名称": cols[0].text.strip(), "条件": cols[1].text.strip(), "描述": " ".join(cols[2].text.strip().split())})

            # --- 潜能解析 ---
            potential_header = soup.find("span", id="潜能提升")
            if potential_header:
                data["潜能"] = []
                current_element = potential_header.find_parent("h2")
                
                # 潜能表格通常只有一个，逻辑可以简化
                search_area = current_element.find_next_sibling()
                if search_area:
                    potential_table = search_area if search_area.name == 'table' else search_area.find('table')
                    if potential_table:
                        for row in potential_table.find_all("tr"):
                            cols = row.find_all(["th", "td"])
                            if len(cols) == 2:
                                data["潜能"].append({"等级": cols[0].text.strip(), "描述": cols[1].text.strip()})

            # --- 技能解析 ---
            skill_header = soup.find("span", id="技能")
            if skill_header:
                current_element = skill_header.find_parent("h2")
                skill_tables = []
                for sibling in current_element.find_next_siblings():
                    if sibling.name == 'h2': break
                    if sibling.name == 'section': # 移动版
                        skill_tables.extend(sibling.find_all('table', class_='wikitable'))
                    elif sibling.name == 'table' and 'wikitable' in sibling.get('class', []): # 桌面版
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
                            skill_levels[level_text] = { "description": " ".join(cols[1].text.strip().split()), "initial_sp": cols[2].text.strip(), "sp_cost": cols[3].text.strip(), "duration": cols[4].text.strip() }
                    skill_data["levels"] = skill_levels
                    data[f"技能{skill_num}"] = skill_data

            return data
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {"error": f"解析本地HTML文件时发生严重错误: {e}"}
        
    def parse_html_desktop(self, html_content):
        """[新增]
        专门解析桌面版PRTS HTML文件的备用函数。
        """
        soup = BeautifulSoup(html_content, "html.parser")
        data = {"attributes": {}, "trust_bonus": {}}
        try:
            # --- 干员名称 (桌面版使用 H1 标签) ---
            name_h1 = soup.find("h1", id="firstHeading")
            if name_h1:
                data["干员名称"] = name_h1.text.strip()
            else:
                raise ValueError("在桌面版HTML中未能找到干员名称")

            # --- 稀有度 (结构通用) ---
            rarity_img = soup.select_one(".charstar img")
            if rarity_img and rarity_img.has_attr("src"):
                rarity_text = rarity_img["src"].split("_")[-1].split(".")[0]
                data["稀有度"] = int(rarity_text) if rarity_text.isdigit() else 6
            
            # --- 职业 (桌面版有明确 class) ---
            class_div = soup.find("div", class_="char-class-text")
            if class_div and class_div.find("a"):
                data["职业"] = class_div.find("a").text.strip()

            # --- 属性 (使用锚点进行稳健查找) ---
            attr_header = soup.find("span", id="属性")
            if attr_header:
                parent_h2 = attr_header.find_parent("h2")
                
                # 攻击间隔, 阻挡数等
                extra_attr_table = parent_h2.find_next("table", class_="char-extra-attr-table")
                if extra_attr_table:
                    # 使用字典映射，兼容不同顺序
                    th_map = {th.text.strip(): td for th, td in zip(extra_attr_table.find_all("th"), extra_attr_table.find_all("td"))}
                    data["再部署时间"] = th_map.get("再部署时间", "").text.strip()
                    data["cost_progression"] = th_map.get("初始部署费用", "").text.strip()
                    data["阻挡数"] = th_map.get("阻挡数", "").text.strip()
                    data["攻击间隔"] = th_map.get("攻击间隔", "").text.strip()
                
                # HP, ATK, DEF, RES
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
                            data["attributes"][attr_key] = [c.text.strip() for c in cols[:-1]]
                            trust_val = cols[-1].text.strip()
                            if trust_val:
                                data["trust_bonus"][attr_key] = trust_val
            
            # --- 特性、天赋、潜能等 (逻辑与之前建议的稳健版相同) ---
            self._parse_html_for_fallback(html_content, data)

            talent_header = soup.find("span", id="天赋")
            if talent_header:
                data["天赋"] = []
                parent_h2 = talent_header.find_parent("h2")
                # 桌面版表格是h2的直接后续兄弟节点
                talent_tables = parent_h2.find_next_siblings("table", class_="wikitable")
                for table in talent_tables:
                    for row in table.find_all("tr")[1:]:
                        cols = row.find_all("td")
                        if len(cols) >= 3 and "备注" not in row.text:
                            data["天赋"].append({
                                "名称": cols[0].text.strip(),
                                "条件": cols[1].text.strip(),
                                "描述": " ".join(cols[2].text.strip().split()),
                            })

            potential_header = soup.find("span", id="潜能提升")
            if potential_header:
                data["潜能"] = []
                parent_h2 = potential_header.find_parent("h2")
                potential_table = parent_h2.find_next_sibling("table", class_="wikitable")
                if potential_table:
                    for row in potential_table.find_all("tr"):
                        cols = row.find_all(["th", "td"])
                        if len(cols) == 2:
                            data["潜能"].append({
                                "等级": cols[0].text.strip(),
                                "描述": cols[1].text.strip(),
                            })
            # ... 此处可以继续补充对技能等其他部分的解析 ...
            return data
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {"error": f"解析桌面版HTML时发生错误: {e}"}