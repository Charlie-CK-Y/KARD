# -*- coding: utf-8 -*-

import time

from odoo import models, api

class ReportResultAnalysis(models.AbstractModel):
    _name = 'report.openkard_research.report_result_analysis'

    def get_total_item(self, data):
        item_search = self.env['kd.result'].search_count(
            [('visit_id','=',data['visit_id'][0])])
        return item_search

    def get_data(self,data):
        result_list = []
        result_search = self.env['kd.result'].search([('visit_id','=',data['visit_id'][0])],order='id')

        if result_search:
            domain_result_item = [('result_id', '=', result_search.id)]
            result_item = self.env['kd.item.line'].sudo().search_read(domain_result_item, \
                                                                      fields=['title','item_id','datalist_id',\
                                                                              'text_type','text_value', \
                                                                              'image_type','image_value', \
                                                                              'date_type','date_value', \
                                                                              'list_type','list_value', \
                                                                              'integer_type','integer_value', \
                                                                              'float_type','float_value', \
                                                                              'char_type','char_value', \
                                                                              'boolean_type','boolean_value', \
                                                                              'time_type','time_value', \
                                                                              'isclose','id'])
            if result_item:
                res = {}
                self.total_item = 0
                for item in result_item:
                    self.total_item += 1
                    if item['text_type'] == True:
                        itemType = 'TEXT'
                        itemValue = item['text_value']
                    elif item['image_type'] == True:
                        itemType = 'IMAGE'
                        itemValue = item['id'] # image value
                    elif item['date_type'] == True:
                        itemType = 'DATE'
                        itemValue = item['date_value']
                    elif item['list_type'] == True:
                        itemType = 'LIST'
                        itemValue = item['list_value']
                    elif item['integer_type'] == True:
                        itemType = 'INT'
                        itemValue = item['integer_value']
                    elif item['float_type'] == True:
                        itemType = 'FLOAT'
                        itemValue = item['float_value']
                    elif item['char_type'] == True:
                        itemType = 'CHAR'
                        itemValue = item['char_value']
                    elif item['boolean_type'] == True:
                        itemType = 'BOOLEAN'
                        itemValue = item['boolean_value']
                    elif item['time_type'] == True:
                        itemType = 'TIME'
                        itemValue = item['time_value']
                    else:
                        itemType = 'UNKNOWN'
                        itemValue = 'n/a'

                    res = {
                        'item_no':str(self.total_item),
                        'item_name':item['item_id'][1],
                        'item_type':itemType,
                        'item_value':itemValue,
                        'isclose':item['isclose']
                    }
                    result_list.append(res)
        return result_list

    @api.model
    def render_html(self,docids,data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        docargs = {
            'doc_ids':self.ids,
            'doc_model':model,
            'docs':docs,
            'time':time,
            'data':data,
            'get_total_item':self.get_total_item(data),
            'get_data':self.get_data(data),
        }
        return self.env['report'].render('openkard_research.report_result_analysis',docargs)