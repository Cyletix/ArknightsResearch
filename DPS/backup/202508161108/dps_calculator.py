# dps_calculator.py (已更新)
import re


class DPSCalculator:
    def calculate_live_stats(self, op_data, elite, level, trust, potential, options):
        # ... (此方法保持不变)
        stats = {}
        key_map_rev = {"hp": "生命上限", "atk": "攻击力", "def": "防御"}
        for attr in ["hp", "atk", "def"]:
            try:
                attr_values = [
                    int(x) for x in op_data.get("attributes", {}).get(attr, ["0"] * 5)
                ]
                if elite + 1 >= len(attr_values):
                    base_stat = attr_values[-1]
                else:
                    min_level_stat, max_level_stat = (
                        attr_values[elite],
                        attr_values[elite + 1],
                    )
                    level_caps = {
                        6: [50, 80, 90],
                        5: [50, 70, 80],
                        4: [45, 60, 70],
                        3: [40, 55, 70],
                        2: [30, 55],
                        1: [30],
                    }
                    max_level_for_elite = level_caps.get(
                        op_data.get("稀有度", 1), [30]
                    )[elite]
                    if level == 1:
                        base_stat = min_level_stat
                    elif level == max_level_for_elite:
                        base_stat = max_level_stat
                    else:
                        base_stat = round(
                            min_level_stat
                            + (max_level_stat - min_level_stat)
                            * (level - 1)
                            / (max_level_for_elite - 1)
                        )
                if options.get("calc_trust"):
                    trust_bonus = int(op_data.get("trust_bonus", {}).get(attr, 0))
                    base_stat += trust_bonus * (trust / 100)
                if options.get("calc_potential"):
                    potential_bonuses = op_data.get("潜能", [])
                    for i in range(potential - 1):
                        if i < len(potential_bonuses):
                            desc = potential_bonuses[i]["描述"]
                            if key_map_rev.get(attr) in desc and "+" in desc:
                                bonus_match = re.search(r"\+(\d+)", desc)
                                if bonus_match:
                                    base_stat += int(bonus_match.group(1))
                stats[attr] = round(base_stat)
            except (IndexError, ValueError, TypeError) as e:
                print(f"Error calculating base stat for {attr}: {e}")
                stats[attr] = 0
        res_values = op_data.get("attributes", {}).get("res", ["0"] * 5)
        stats["res"] = (
            int(res_values[elite + 1])
            if len(res_values) > elite + 1
            else (int(res_values[-1]) if res_values else 0)
        )
        return stats

    def calculate_dps(self, op_data, live_stats, skill_choice, enemy_stats, all_buffs):
        """
        [REWRITTEN] 遵循PRTS公式重写的核心DPS计算函数
        """
        # 1. 初始属性
        base_atk = live_stats.get("atk", 0)
        base_atk_interval = float(op_data.get("攻击间隔", "1").replace("s", ""))
        enemy_def = enemy_stats.get("def", 0)
        enemy_res = enemy_stats.get("res", 0)

        # 2. 汇总所有来源的Buff
        # 【BUG修复】在此处补全所有可能从UI传入的键，以防止KeyError
        total_buffs = {
            "direct_atk_flat": 0,
            "direct_atk_pct": 0,
            "final_atk_flat": 0,
            "direct_def_flat": 0,   # 补全
            "direct_def_pct": 0,    # 补全
            "final_def_flat": 0,    # 补全
            "aspd": 0,
            "interval": 0.0,
            "phys_dmg_mult": 1.0,
            "arts_dmg_mult": 1.0,
        }
        
        for buff_source in all_buffs.values():
            for key, value in buff_source.items():
                if "mult" in key:  # 伤害倍率是乘算
                    total_buffs[key] *= value / 100.0
                else:  # 其他是加算
                    total_buffs[key] += value

        # 3. 应用属性基本公式计算最终攻击力
        # Af = Ft * [(A + Dp) * (1 + Dt) + Fp]
        # 注: 此处简化了Ft(最终乘算)，因为它极少见且通常用于debuff。
        # A (基础攻击力)
        A = base_atk
        # Dp (直接加算)
        Dp = total_buffs["direct_atk_flat"]
        # Dt (直接乘算)
        Dt = total_buffs["direct_atk_pct"] / 100.0
        # Fp (最终加算 / 鼓舞)
        Fp = total_buffs["final_atk_flat"]

        final_atk = (A + Dp) * (1 + Dt) + Fp

        # 4. 计算最终攻击间隔 (攻速公式)
        # T = T0 / (CLAMP(S, 10, 600) / 100)
        S = 100 + total_buffs["aspd"]
        clamped_aspd = min(max(S, 10), 600)
        T0 = base_atk_interval - total_buffs["interval"]
        actual_atk_interval = (
            T0 / (clamped_aspd / 100.0) if clamped_aspd > 0 else float("inf")
        )

        # 5. 计算单次伤害 (伤害公式)
        damage_type = "法术" if "法术伤害" in op_data.get("特性-描述", "") else "物理"

        base_phys_damage = 0
        base_arts_damage = 0

        if damage_type == "物理":
            base_phys_damage = max(final_atk - enemy_def, final_atk * 0.05)
        else:  # 法术
            base_arts_damage = final_atk * max(0, (100 - enemy_res) / 100.0)

        final_phys_damage = base_phys_damage * total_buffs["phys_dmg_mult"]
        final_arts_damage = base_arts_damage * total_buffs["arts_dmg_mult"]

        total_damage_per_hit = final_phys_damage + final_arts_damage

        # 6. 计算最终DPS
        dps = (
            total_damage_per_hit / actual_atk_interval
            if actual_atk_interval > 0
            else float("inf")
        )

        # 7. 格式化输出
        result_text = f"--- {skill_choice} ---\n"
        result_text += f"基础攻击力: {A:.0f}\n"
        result_text += f"总直接加算(Dp): +{Dp}, 总直接乘算(Dt): +{Dt*100:.0f}%\n"
        result_text += f"总最终加算(Fp): +{Fp} (鼓舞)\n"
        result_text += f"最终攻击力: {final_atk:.1f}\n"
        result_text += "----\n"
        result_text += f"最终攻击速度: {clamped_aspd:.0f}\n"
        result_text += f"最终攻击间隔: {actual_atk_interval:.3f}s\n"
        result_text += "----\n"
        result_text += f"伤害类型: {damage_type}\n"
        result_text += f"物理/法术伤害倍率: {total_buffs['phys_dmg_mult']:.2f} / {total_buffs['arts_dmg_mult']:.2f}\n"
        result_text += (
            f"单次伤害 (对 {enemy_def}防 {enemy_res}抗): {total_damage_per_hit:.1f}\n"
        )
        result_text += f"总计DPS: {dps:.1f}\n"

        return result_text