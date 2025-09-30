import re
from collections import defaultdict

class OxidationStateAnalyzer:
    def __init__(self):
        # 주기율표 모든 원소의 일반적인 산화상태 규칙
        self.oxidation_rules = {
            # 1족 - 알칼리 금속
            'H': [1, -1],  # 수소는 특별한 경우
            'Li': [1], 'Na': [1], 'K': [1], 'Rb': [1], 'Cs': [1], 'Fr': [1],
            
            # 2족 - 알칼리 토금속
            'Be': [2], 'Mg': [2], 'Ca': [2], 'Sr': [2], 'Ba': [2], 'Ra': [2],
            
            # 3족
            'Sc': [3], 'Y': [3],
            
            # 4족
            'Ti': [2, 3, 4], 'Zr': [4], 'Hf': [4], 'Rf': [4],
            
            # 5족
            'V': [2, 3, 4, 5], 'Nb': [3, 5], 'Ta': [5], 'Db': [5],
            
            # 6족
            'Cr': [2, 3, 6], 'Mo': [2, 3, 4, 5, 6], 'W': [2, 3, 4, 5, 6], 'Sg': [6],
            
            # 7족
            'Mn': [2, 3, 4, 6, 7], 'Tc': [4, 7], 'Re': [4, 7], 'Bh': [7],
            
            # 8족
            'Fe': [2, 3, 6], 'Ru': [2, 3, 4, 8], 'Os': [2, 3, 4, 8], 'Hs': [8],
            
            # 9족
            'Co': [2, 3], 'Rh': [3], 'Ir': [3, 4], 'Mt': [3],
            
            # 10족
            'Ni': [2, 3], 'Pd': [2, 4], 'Pt': [2, 4], 'Ds': [2],
            
            # 11족
            'Cu': [1, 2], 'Ag': [1], 'Au': [1, 3], 'Rg': [1, 3],
            
            # 12족
            'Zn': [2], 'Cd': [2], 'Hg': [1, 2], 'Cn': [2],
            
            # 13족 - 붕소족
            'B': [3], 'Al': [3], 'Ga': [3], 'In': [1, 3], 'Tl': [1, 3], 'Nh': [3],
            
            # 14족 - 탄소족
            'C': [-4, -3, -2, -1, 2, 4], 'Si': [4], 'Ge': [2, 4], 'Sn': [2, 4], 'Pb': [2, 4], 'Fl': [2, 4],
            
            # 15족 - 질소족
            'N': [-3, -2, -1, 1, 2, 3, 4, 5], 'P': [-3, 3, 5], 'As': [-3, 3, 5], 
            'Sb': [-3, 3, 5], 'Bi': [3, 5], 'Mc': [3],
            
            # 16족 - 산소족
            'O': [-2, -1], 'S': [-2, 2, 4, 6], 'Se': [-2, 2, 4, 6], 
            'Te': [-2, 2, 4, 6], 'Po': [2, 4], 'Lv': [2, 4],
            
            # 17족 - 할로겐
            'F': [-1],  # 플루오린은 항상 -1
            'Cl': [-1, 1, 3, 5, 7], 'Br': [-1, 1, 3, 5, 7], 'I': [-1, 1, 3, 5, 7],
            'At': [-1, 1, 3, 5, 7], 'Ts': [-1, 1, 3, 5, 7],
            
            # 18족 - 희가스 (일반적으로 0가이지만 일부 화합물 형성 가능)
            'He': [0], 'Ne': [0], 'Ar': [0], 'Kr': [2], 'Xe': [2, 4, 6, 8], 'Rn': [2], 'Og': [0],
            
            # 란탄족 (Lanthanides) - 주로 +3가
            'La': [3], 'Ce': [3, 4], 'Pr': [3, 4], 'Nd': [3], 'Pm': [3], 'Sm': [2, 3],
            'Eu': [2, 3], 'Gd': [3], 'Tb': [3, 4], 'Dy': [3], 'Ho': [3], 'Er': [3],
            'Tm': [2, 3], 'Yb': [2, 3], 'Lu': [3],
            
            # 악티늄족 (Actinides)
            'Ac': [3], 'Th': [4], 'Pa': [4, 5], 'U': [3, 4, 5, 6], 'Np': [3, 4, 5, 6, 7],
            'Pu': [3, 4, 5, 6], 'Am': [3, 4, 5, 6], 'Cm': [3, 4], 'Bk': [3, 4],
            'Cf': [3], 'Es': [3], 'Fm': [3], 'Md': [3], 'No': [2, 3], 'Lr': [3],
        }
        
        # 원소의 전기음성도 기반 우선순위 (산화상태 결정시 참고용)
        self.electronegativity = {
            'F': 4.0, 'O': 3.44, 'N': 3.04, 'Cl': 3.16, 'Br': 2.96, 'I': 2.66,
            'S': 2.58, 'C': 2.55, 'P': 2.19, 'H': 2.20, 'Se': 2.55, 'As': 2.18,
            'Te': 2.1, 'Sb': 2.05, 'Si': 1.90, 'B': 2.04, 'Ge': 2.01, 'Sn': 1.96,
            'Pb': 2.33, 'Al': 1.61, 'Ga': 1.81, 'In': 1.78, 'Tl': 1.62,
            # 금속들은 일반적으로 낮은 전기음성도
            'Li': 0.98, 'Na': 0.93, 'K': 0.82, 'Rb': 0.82, 'Cs': 0.79,
            'Be': 1.57, 'Mg': 1.31, 'Ca': 1.00, 'Sr': 0.95, 'Ba': 0.89,
            'Sc': 1.36, 'Ti': 1.54, 'V': 1.63, 'Cr': 1.66, 'Mn': 1.55,
            'Fe': 1.83, 'Co': 1.88, 'Ni': 1.91, 'Cu': 1.90, 'Zn': 1.65,
        }
    
    def parse_formula(self, formula):
        """화학식을 파싱하여 원소와 개수를 추출"""
        # 괄호 처리를 위한 정규식
        pattern = r'([A-Z][a-z]?)(\d*)'
        elements = defaultdict(int)
        
        # 간단한 괄호 처리
        formula = self._expand_parentheses(formula)
        
        matches = re.findall(pattern, formula)
        for element, count in matches:
            count = int(count) if count else 1
            elements[element] += count
            
        return dict(elements)
    
    def _expand_parentheses(self, formula):
        """괄호가 있는 화학식 처리"""
        while '(' in formula:
            # 가장 안쪽 괄호부터 처리
            start = formula.rfind('(')
            if start == -1:
                break
            end = formula.find(')', start)
            if end == -1:
                break
                
            # 괄호 다음의 숫자 찾기
            multiplier_match = re.match(r'(\d+)', formula[end+1:])
            multiplier = int(multiplier_match.group(1)) if multiplier_match else 1
            
            # 괄호 안의 내용 처리
            inside = formula[start+1:end]
            expanded = ""
            
            pattern = r'([A-Z][a-z]?)(\d*)'
            for element, count in re.findall(pattern, inside):
                count = int(count) if count else 1
                new_count = count * multiplier
                expanded += element + (str(new_count) if new_count > 1 else "")
            
            # 원래 공식에서 괄호 부분을 확장된 것으로 대체
            end_pos = end + 1 + (len(multiplier_match.group(1)) if multiplier_match else 0)
            formula = formula[:start] + expanded + formula[end_pos:]
            
        return formula
    
    def get_possible_oxidation_states(self, elements):
        """각 원소의 가능한 산화상태 조합을 생성 (최적화된 버전)"""
        element_list = list(elements.keys())
        
        # 원소가 너무 많으면 일반적인 산화상태만 사용
        if len(element_list) > 4:
            return self._get_common_oxidation_combinations(elements)
        
        oxidation_combinations = []
        
        def generate_combinations(idx, current_combination):
            if idx == len(element_list):
                oxidation_combinations.append(current_combination.copy())
                return
            
            # 너무 많은 조합을 방지하기 위해 제한
            if len(oxidation_combinations) > 1000:
                return
            
            element = element_list[idx]
            possible_states = self.oxidation_rules.get(element, [1, 2, 3, -1, -2])
            
            # 가장 일반적인 산화상태부터 시도
            possible_states = self._sort_by_probability(element, possible_states)
            
            for state in possible_states[:5]:  # 최대 5개 상태만 고려
                current_combination[element] = state
                generate_combinations(idx + 1, current_combination)
        
        generate_combinations(0, {})
        return oxidation_combinations
    
    def _get_common_oxidation_combinations(self, elements):
        """복잡한 화합물의 경우 일반적인 산화상태 조합만 반환"""
        combinations = []
        common_states = {}
        
        for element in elements:
            if element in self.oxidation_rules:
                states = self.oxidation_rules[element]
                # 가장 일반적인 상태 선택
                if len(states) == 1:
                    common_states[element] = states[0]
                else:
                    # 전기음성도 기반으로 일반적인 상태 선택
                    common_states[element] = self._get_most_common_state(element, states)
            else:
                # 알려지지 않은 원소는 기본값 사용
                common_states[element] = 2 if element not in ['H', 'F', 'Cl', 'Br', 'I'] else -1
        
        combinations.append(common_states)
        return combinations
    
    def _get_most_common_state(self, element, states):
        """원소의 가장 일반적인 산화상태 반환"""
        # 특별한 규칙들
        special_rules = {
            'O': -2, 'H': 1, 'F': -1, 'Cl': -1, 'Br': -1, 'I': -1,
            'Na': 1, 'K': 1, 'Ca': 2, 'Mg': 2, 'Al': 3, 'Fe': 3, 'Cu': 2
        }
        
        if element in special_rules:
            return special_rules[element]
        
        # 그 외의 경우 가장 일반적인 상태 반환
        if 3 in states:
            return 3
        elif 2 in states:
            return 2
        else:
            return states[0]
    
    def _sort_by_probability(self, element, states):
        """산화상태를 확률 기반으로 정렬"""
        # 일반적인 산화상태 우선순위
        priority_order = {
            'O': [-2, -1], 'H': [1, -1], 'F': [-1],
            'Cl': [-1, 1, 3, 5, 7], 'Br': [-1, 1, 3, 5, 7], 'I': [-1, 1, 3, 5, 7],
            'S': [-2, 6, 4, 2], 'N': [-3, 3, 5, -1, 1, 2, 4],
            'C': [4, -4, 2, -2, -1, -3], 'P': [5, 3, -3],
            'Fe': [3, 2, 6], 'Cu': [2, 1], 'Al': [3], 'Ca': [2], 'Na': [1], 'K': [1]
        }
        
        if element in priority_order:
            ordered_states = []
            for state in priority_order[element]:
                if state in states:
                    ordered_states.append(state)
            # 남은 상태들 추가
            for state in states:
                if state not in ordered_states:
                    ordered_states.append(state)
            return ordered_states
        
        return sorted(states, key=lambda x: abs(x))  # 절댓값이 작은 것부터
    
    def calculate_total_charge(self, elements, oxidation_states):
        """주어진 산화상태에서 총 전하 계산"""
        total_charge = 0
        for element, count in elements.items():
            oxidation_state = oxidation_states.get(element, 0)
            total_charge += oxidation_state * count
        return total_charge
    
    def is_neutral_compound(self, formula):
        """화합물이 중성인지 확인"""
        elements = self.parse_formula(formula)
        
        # 알려지지 않은 원소가 있는지 확인
        unknown_elements = [elem for elem in elements if elem not in self.oxidation_rules]
        if unknown_elements:
            print(f"  경고: 알려지지 않은 원소 {unknown_elements} - 기본 산화상태 사용")
        
        # 특별한 경우들 처리
        if self._is_special_case(formula, elements):
            return True, None
        
        oxidation_combinations = self.get_possible_oxidation_states(elements)
        
        for oxidation_states in oxidation_combinations:
            total_charge = self.calculate_total_charge(elements, oxidation_states)
            if total_charge == 0:
                return True, oxidation_states
        
        return False, None
    
    def _is_special_case(self, formula, elements):
        """특별한 경우들 (단원소 물질, 합금 등) 처리"""
        # 단원소 물질들 (원소 상태)
        if len(elements) == 1:
            element = list(elements.keys())[0]
            # 이원자 분자들
            diatomic_elements = ['H', 'N', 'O', 'F', 'Cl', 'Br', 'I']
            if element in diatomic_elements and elements[element] == 2:
                return True
            # 단원자 희가스
            noble_gases = ['He', 'Ne', 'Ar', 'Kr', 'Xe', 'Rn', 'Og']
            if element in noble_gases and elements[element] == 1:
                return True
            # 금속 원소들 (단체)
            metals = ['Li', 'Na', 'K', 'Rb', 'Cs', 'Fr', 'Be', 'Mg', 'Ca', 'Sr', 'Ba', 'Ra',
                     'Al', 'Ga', 'In', 'Tl', 'Sn', 'Pb', 'Bi', 'Po', 'Fe', 'Cu', 'Ag', 'Au', 'Zn']
            if element in metals:
                return True
        
        return False

