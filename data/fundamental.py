"""
基本面数据模块
获取A股基本面数据
"""

import baostock as bs
import pandas as pd
from typing import Optional, Dict


class FundamentalData:
    """基本面数据获取"""

    def __init__(self):
        self._bs_login = False

    def _login(self):
        if not self._bs_login:
            bs.login()
            self._bs_login = True

    def _logout(self):
        if self._bs_login:
            bs.logout()
            self._bs_login = True

    def get_stock_basic(self, code: str) -> Optional[Dict]:
        """获取股票基本信息"""
        self._login()
        bs_code = f"sh.{code}" if code.startswith('6') else f"sz.{code}"
        rs = bs.query_stock_basic(code=bs_code)

        data = []
        while rs.next():
            data.append(rs.get_row_data())

        if not data:
            return None

        fields = ['code', 'code_name', 'ipoDate', 'outDate', 'type', 'status']
        result = dict(zip(fields, data[0]))
        self._logout()
        return result

    def get_profit_data(self, code: str, year: int = 2024, quarter: int = 4) -> Optional[Dict]:
        """获取利润数据"""
        self._login()
        bs_code = f"sh.{code}" if code.startswith('6') else f"sz.{code}"
        rs = bs.query_profit_data(code=bs_code, year=year, quarter=quarter)

        data = []
        while rs.next():
            data.append(rs.get_row_data())

        self._logout()
        if not data:
            return None

        result = dict(zip(rs.fields, data[0]))
        return result

    def get_operation_data(self, code: str, year: int = 2024, quarter: int = 4) -> Optional[Dict]:
        """获取经营数据"""
        self._login()
        bs_code = f"sh.{code}" if code.startswith('6') else f"sz.{code}"
        rs = bs.query_operation_data(code=bs_code, year=year, quarter=quarter)

        data = []
        while rs.next():
            data.append(rs.get_row_data())

        self._logout()
        if not data:
            return None

        result = dict(zip(rs.fields, data[0]))
        return result

    def get_dupont_data(self, code: str, year: int = 2024, quarter: int = 4) -> Optional[Dict]:
        """获取杜邦数据"""
        self._login()
        bs_code = f"sh.{code}" if code.startswith('6') else f"sz.{code}"
        rs = bs.query_dupont_data(code=bs_code, year=year, quarter=quarter)

        data = []
        while rs.next():
            data.append(rs.get_row_data())

        self._logout()
        if not data:
            return None

        result = dict(zip(rs.fields, data[0]))
        return result


def get_fundamental(code: str, year: int = 2024, quarter: int = 4) -> Dict:
    """获取股票基本面数据"""
    fd = FundamentalData()
    result = {}

    # 基本信息
    basic = fd.get_stock_basic(code)
    if basic:
        result.update(basic)

    # 利润数据
    profit = fd.get_profit_data(code, year, quarter)
    if profit:
        result.update(profit)

    # 经营数据
    operation = fd.get_operation_data(code, year, quarter)
    if operation:
        result.update(operation)

    return result


if __name__ == '__main__':
    print("=" * 50)
    print("基本面数据测试")
    print("=" * 50)

    result = get_fundamental('600519', 2024, 4)
    print("\n茅台（600519）基本面:")
    for k, v in result.items():
        print(f"  {k}: {v}")
