# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class KdItem(models.Model):
    _inherit = 'mail.thread'
    _name = 'kd.item'
    _rec_name = 'name'

    name = fields.Char('Name', required=True)
    data_type = fields.Selection([('integer', '숫자-정수'), ('float', '숫자-실수'), ('char', '문자'), \
                                  ('date', '날짜'), ('time', '시간'), ('selection', '목록'), ('boolean', '논리'), \
                                  ('text', '텍스트'), ('image', '이미지')], 'Type', required=True)
    state = fields.Selection([('preparing', 'Preparing'), ('available', 'Available'), ('issue', 'Issued')], 'State', \
                             default='preparing', track_visibility='onchange')
    data_size = fields.Integer('Size/Length', default=0)
    default_value = fields.Char('Default',default='0')
    is_mandatory = fields.Boolean('Mandatory',default=False)
    left_right_division = fields.Selection([('R','right'),('L','left'),('N','None')],'Left or Right',default="N")
    maximum_value = fields.Float('Max limit',default=0)
    minimum_value = fields.Float('Min limit',default=0)
    unit = fields.Char('Unit')
    description = fields.Text('Description')

    datalist_id = fields.Many2one('kd.datalist', 'List Data')

    @api.model
    def create(self, vals):
        if vals.get('data_type') =='integer':
            if 'maximum_value' in vals:

                min = int(vals.get('minimum_value'))
                max = int(vals.get('maximum_value'))

                if max > 9999999:
                    raise ValidationError(_('Error: Maximum input range exceeded[9,999,999]'))

                if min < 0:
                    raise ValidationError(_('Error: Minimum input range exceeded[0.01]'))

                if  min >= max:
                    raise ValidationError(_('Error: The minimum value is greater than the maximum value.'))

                if max <= min:
                    raise ValidationError(_('Error: The minimum value is greater than the maximum value.'))

        if vals.get('data_type') == 'char':
            if 'data_size' in vals:
                if 'maximum_value' in vals:
                    if int(vals.get('data_size')) > 300:
                        raise ValidationError(_('Error: The minimum char size/length is greater than the 300.'))

        return super(KdItem, self).create(vals)

    @api.multi
    def write(self, vals):
        if vals.get('data_type') == 'integer':
            if 'maximum_value' in vals:

                min = int(vals.get('minimum_value'))
                max = int(vals.get('maximum_value'))

                if max > 9999999:
                    raise ValidationError(_('Error: Maximum input range exceeded[9,999,999]'))

                if min < 0:
                    raise ValidationError(_('Error: Minimum input range exceeded[0.01]'))

                if  min >= max:
                    raise ValidationError(_('Error: The minimum value is greater than the maximum value.'))

                if max <= min:
                    raise ValidationError(_('Error: The minimum value is greater than the maximum value.'))

        return super(KdItem, self).write(vals)


    class KdItemLine(models.Model):
        _name = 'kd.item.line'
        _rec_name = 'item_id'

        item_id = fields.Many2one('kd.item', '검사 속성', required=True)


    class KdDataList(models.Model):
        _name = 'kd.datalist'
        _rec_name = 'title'

        name = fields.Char(string='Value list',default='예) 서울,부산,대구')
        title = fields.Char(string='Title')
        default_value = fields.Char(string='Default value')
