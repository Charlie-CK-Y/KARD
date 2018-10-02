# -*- coding: utf-8 -*-

from odoo import models,fields,api

class KdItemLine(models.Model):
    '''
    OpenKard Item을 참조하려면 _inherit를 사용 해야 한다.
    '''
    _inherit = 'kd.item.line'

    result_id = fields.Many2one('kd.result','Result(s)',required=True)
    datalist_id = fields.Many2one('kd.item.line.datalist', 'list')

    @api.multi
    def write(self, vals):
        itemSourceSchema = ['is_mandatory', 'data_type', 'default_value', 'datalist_id','maximum_value','minimum_value']

        return super(KdItemLine, self).write(vals)


class KdItemlineDatalist(models.Model):
    _name = 'kd.item.line.datalist'
    _description = 'item line selection list'
    _rec_name = 'name'

    title = fields.Char(string='List Title')
    name = fields.Text(string='List Value',default='예)서울,부산,대구')
    value = fields.Char(string='Result Code',default='n/a')
    # OpenKard Item에서 생성한 Item
    item_id = fields.Integer(string='source item id',default=-1)

    # 다른 쪽을 참조하고 있는 테이블
    # 사용하는쪽_이름+s = fields.One2many('참조하는쪽','사용하는쪽_id','사용하는이름(s)'
    itemlineIds = fields.One2many('kd.item.line','datalist_id', 'Result Data List')


