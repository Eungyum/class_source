import cx_Oracle as cx
from prettytable import PrettyTable

class DBconnection:
    
    def __init__(self, user, password, tab=None, value=None):
        self.user = user
        self.password = password
        self.dns = "localhost:1521/xe"
        self.tab = tab
        self.value = value
        self.conn = None
        self.cursor = None
        self.tab_col_names = []
        self.conditions = {}
        self.ch = None
        self.tab_col_names = None

        try:
            self.conn = cx.connect(self.user, self.password, self.dns)
            self.cursor = self.conn.cursor()
            self.cursor.execute(f"SELECT * FROM {self.tab}")
            self.tab_col_names = [desc[0] for desc in self.cursor.description]

        except Exception:
            print("에러입니다.")
        except cx.DatabaseError as e1:
            print("\nDB 접속에 실패했습니다.")
            print("아이디와 비밀번호를 다시 확인해 주세요.")
            self.conn = None
            self.cursor = None
            print("self.conn")
            exit(1)
            
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.conn:
            self.conn.close()
          
    def choice(self, selec_cols):
        self.selec_cols=selec_cols
        if self.value == "1":
            self.look()
        elif self.value == "2":
            self.insert()
        elif self.value == "3":
            self.update()
        else:
            pass
#-----------------------------------------------------------------------------------------------------------------------------                     
    def look(self):
        print("검색 조건 입력\n(공백입력시 전체 테이블 조회)")
        valid_conditions = {}
        for col_name in self.tab_col_names:
            valu = input(f"{col_name} (없으면 Enter): ").strip()
            if valu:
                valid_conditions[col_name] = valu

        if valid_conditions:
            condition_str = " AND ".join([f"{col_name} LIKE :{col_name}" for col_name in valid_conditions])
            query = f"SELECT * FROM {self.tab} WHERE {condition_str}"
        else:
            query = f"SELECT * FROM {self.tab}"
        try:
            self.cursor.execute(query, valid_conditions)
            rows = self.cursor.fetchall()

            if not rows:
                print("검색 결과가 없습니다.")
            else:
                table = PrettyTable()
                table.field_names = self.tab_col_names
                for row in rows:
                    table.add_row(row)
                print(table)

        except cx.DatabaseError as e:
            print("데이터베이스 오류:", e)
        except Exception as e:
            print("오류 발생:", e)       
#-----------------------------------------------------------------------------------------------------------------------------   
    def insert(self):        
        print(self.selec_cols)
    
        input_values = {}
        valid_columns = []

        for col in self.selec_cols:
            val = input(f"{col}: ")
            if val:
                input_values[col] = val
                valid_columns.append(col)
            
        if not valid_columns:
            print("입력된 데이터가 없습니다.")
            return
        
        columns = ', '.join(valid_columns) 

        set_statement = ', '.join([f":{col}" for col in valid_columns])
        query = f"INSERT INTO {self.tab} ({columns}) VALUES ({set_statement})"
    
        try:
            self.cursor.execute(query, input_values)
            self.cursor.connection.commit()
            print(f"{self.tab}에 레코드가 추가되었습니다.")
        except Exception as e:
            print("데이터 삽입 중 오류 발생", e)           
#-----------------------------------------------------------------------------------------------------------------------------          
    def update(self):
        print(self.selec_cols)
        serial_no = input("상품 시리얼 넘버 : ")

        input_values = {}
        valid_columns = []
    
        for col in self.selec_cols:
            val = input(f"{col}: ")
            if val:
                input_values[col] = val
                valid_columns.append(col)

        set_statement = ', '.join([f":{col}" for col in input_values])
        valid_columns_str = ', '.join(valid_columns)  # 유효한 컬럼들을 문자열로 변환
        query = f"UPDATE {self.tab} SET {valid_columns_str} = {set_statement} WHERE serial_no = :serial_no"  
    
        input_values["serial_no"] = serial_no
    
        try:
            self.cursor.execute(query, input_values)
            self.cursor.connection.commit()
            print(f"{serial_no}의 정보가 변경되었습니다.")
        except Exception as e5:
            print("잘못된 입력입니다.")
#-----------------------------------------------------------------------------------------------------------------------------   
def main():
    print("\n\n\n---------------재고관리 프로그램---------------")
    
    user = input("DB 아이디: ")
    password = input("DB 비밀번호: ")
    while True:
        print("---------------   메인 프로그램   ---------------")
        print("\n1.매입::2.매출::3.재고상품::4.취급상품::5.종료\n")
        ch = input("입력 : ")     
        if ch == "1":
            value = input("\n\n\n---------------- 매입관리창 ----------------\n1.매입기록 조회::2.매입기록 입력::3.매입기록 수정\n : ")
            with DBconnection(user, password, tab="pur", value=value) as purchase:
                purchase.choice(selec_cols=["serial_no", "pq", "pcost", "siz", "broker", "discount"])
        elif ch == "2":
            value = input("\n\n\n---------------- 매출관리창 ----------------\n1.매출기록 조회::2.매출기록 입력::3.매출기록 수정\n : ")
            with DBconnection(user, password, tab="sal",  value=value) as sales:
                sales.choice(selec_cols=["serial_no", "sq", "turnover"])
        elif ch == "3":
            value = input("\n\n\n---------------- 재고관리창 ----------------\n1.재고상품 조회::2.재고상품 입력::3.재고상품 수정\n : ")
            with DBconnection(user, password, tab="inven", value=value) as inventory:
                inventory.choice(selec_cols=["serial_no", "quan", "tcost", "brand", "ptype"])
        elif ch == "4":
            value = input("\n\n\n---------------- 취급상품창 ----------------\n1.취급상품 조회::2.취급상품 입력::3.취급상품 수정\n : ")
            with DBconnection(user, password, tab="pro_info", value=value) as product_info:
                product_info.choice(selec_cols=["serial_no", "brand", "pname", "ptype", "siz", "country", "color", "euro"])
        elif ch == "5":
            print("프로그램 종료")
            break
        else:
            print("1, 2, 3, 4, 5 중에서 선택하세요.")
                
if __name__ == "__main__":
    main()