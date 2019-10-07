'''
  reads beancount's data file and returns pandas' dataframe
'''

import datetime
import beancount
from beancount.query import query

import pandas as pd

class BeanPandas():
    def __init__(self, input_file):
        self._entries, self._errors, self._options_map = beancount.loader.load_file(input_file)

    def query(self, query_str, *args):
        '''read doc for run_query in /usr/lib/python3.7/site-packages/beancount/query/query.py
          query('select date,account,number where account~{} and year ={}",'"assets"','2016')
        '''
        return query.run_query(self._entries, self._options_map, query_str, *args)

    def query2pd(self, query_str, *args):
        '''
        same functionality as 'query' method; output is converted to proper DataFrame
        Limitations:
          - inventory type is not handled (convert it into decimal in query)
        '''
        dt_types, dt_records = self.query(query_str, *args)

        col_names, col_types = zip(*dt_types)
        col_names = list(col_names)
        #df_data = {a:[] for a in col_names}
        df_data = []
        for r in dt_records:
            r_vals = []
            for i,c in enumerate(r):
                r_vals.append(self._convert_from_bean(c, col_types[i]))
            df_data.extend(self._get_rows(r_vals))
        if not df_data:
            return None
        self._split_columns(df_data, col_names)

        return pd.DataFrame(df_data, columns=col_names)
        #return(col_names,col_types,df_data)

    def _split_columns(self, df_data, col_names):
        '''split columns with colmplex values (tuples)
        '''
        def get_subitem(item, item_no):
            if isinstance(item, tuple):
                return item[item_no]
            else:
                return item

        #analyze dataset and collect indexes for columns with tuples
        column_index_tuple = {}
        for i, col in enumerate(df_data[0]):
            for r in df_data:
                if r[i] is None:
                    continue
                elif isinstance(r[i], tuple):
                    column_index_tuple[i] = len(r[i])

        indexes = sorted(column_index_tuple.keys(), reverse=True)
        indexes_done = []
        for col in indexes:
            for r in df_data:
                val = r[col]
                for item_no in range(column_index_tuple[col]):
                    if item_no == 0:
                        r[col] = get_subitem(val, item_no)
                    else:
                        r.insert(col+item_no, get_subitem(val, item_no))
                        if col not in indexes_done:
                            col_names.insert(col+item_no,'{}_{}'.format(col_names[col],item_no))
                            indexes_done.append(col)

    def _get_rows(self, r_vals):
        'multiply rows if any value contains array'
        rows = []
        list_value_index = []
        max_n_values = 1
        for i,val in enumerate(r_vals):
            if isinstance(val, list):
                list_value_index.append(i)
                max_n_values = max(max_n_values, len(val))

        for n in range(max_n_values):
            rows.append(r_vals.copy())

#        if max_n_values > 1:
        for i in list_value_index:
            value_to_split = rows[0][i]
            for n,r in enumerate(rows):
                if value_to_split:
                    r[i] = value_to_split[n]
                else:
                    r[i] = None

        return rows

    def _convert_from_bean(self, val, col_type):
        '''
        converts data from beancount object to pandas types
        if returns array - calling function spawns extra copies of row for each value
        if returns tuple - calling function splits the column
        '''
        if col_type is str:
            return val
        elif col_type is beancount.core.inventory.Inventory:
            return_val = []
            for position in val.get_positions():
                return_val.append(self._convert_from_bean(position, beancount.core.position.Position))
            return return_val
        elif col_type is beancount.core.position.Position:
            amount, curr  = val[0]
            return (float(amount), curr)
        elif col_type is datetime.date:
            return val
        else:
            return val
