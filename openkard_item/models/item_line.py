# -*- coding: utf-8 -*-
from datetime import timedelta, date, datetime

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class KdItemLine(models.Model):
    _name = 'kd.item.line'
    _rec_name = 'name'
    # -------------------------------------------------------------------------------------------------------------------
    # 검사 항목 필드
    # -------------------------------------------------------------------------------------------------------------------
    item_id = fields.Many2one('kd.item', 'Item', required=True)
    # -------------------------------------------------------------------------------------------------------------------
    # 검사 양식 필드
    # -------------------------------------------------------------------------------------------------------------------
    name = fields.Char('항목명칭', required=True,readonly=True,related='item_id.name')
    default_value = fields.Char('기본값', default='0',readonly=True,related='item_id.default_value')
    is_mandatory = fields.Boolean('필수입력', default=False,readonly=True,related='item_id.is_mandatory')
    left_right_division = fields.Selection([('R', 'right'), ('L', 'left'), ('N', 'None')], '좌우구분', default="N",readonly=True,related='item_id.left_right_division')
    maximum_value = fields.Float('최대값', default=0,readonly=True,related='item_id.maximum_value')
    minimum_value = fields.Float('최소값', default=0,readonly=True,related='item_id.minimum_value')
    unit = fields.Char('단위',readonly=True,related='item_id.unit')
    data_size = fields.Integer('테이터 크기', required=True, default=0,readonly=True,related='item_id.data_size')
    data_type = fields.Selection([('integer', '숫자-정수'), ('float', '숫자-실수'), ('char', '문자'), \
                                  ('date', '날짜'), ('time', '시간'), ('selection', '목록'), ('boolean', '논리'), \
                                  ('text', '텍스트'), ('image', '이미지')], 'type', required=True,related='item_id.data_type')

    state = fields.Selection([('preparing', 'Preparing'), ('available', 'Available'), ('issue', 'Issued')],
                             default="preparing", required='True', string='발행여부', track_visibility='onchange',readonly=True,related='item_id.state')
    description = fields.Text('설명',readonly=True,related='item_id.description')
    # -------------------------------------------------------------------------------------------------------------------
    # 검사 양식의 목록 필드
    # -------------------------------------------------------------------------------------------------------------------
    datalist_id = fields.Many2one('kd.item.line.datalist', '검사 양식 목록')
    # -------------------------------------------------------------------------------------------------------------------
    # 검사 결과 필드
    #-------------------------------------------------------------------------------------------------------------------
    # 1. 텍스트 결과
    text_value = fields.Text('Text')
    text_type = fields.Boolean(default=False, string="텍스트")
    # 2. 이미지 결과
    image_value = fields.Binary(attachment=True, string="Image")
    image_type = fields.Boolean(default=False, string="이미지")
    # 3. 날짜 결과
    date_value = fields.Date(string="Date")
    date_type = fields.Boolean(default=False, string="날짜")

    # 4. 목록 결과
    list_value = fields.Text(string='List',default='n/a')
    list_type = fields.Boolean(default=False, string="목록")
    # 5. 숫자 결과(정수)
    integer_value = fields.Integer(string='Integer', default=0)
    integer_type = fields.Boolean(default=False, string="정수")
    # 6. 숫자 결과(실수)
    float_value = fields.Float(string='Float', default=0)
    float_type = fields.Boolean(default=False, string="실수")
    # 7. 문자 결과
    char_value = fields.Char(string='Char', default='n/a', size=250)
    char_type = fields.Boolean(default=False, string="문자(300자 이내)")
    # 8. 시간 결과
    time_value = fields.Char(string='Time', default='00:00',size=5)
    time_type = fields.Boolean(default=False, string="시간")
    # 9. 논리 결과
    boolean_value = fields.Boolean(string='Logical', default=False)
    boolean_type = fields.Boolean(default=False, string="논리")
    isclose = fields.Boolean(default=False,string="Completed")
    # is_valid = fields.Boolean(default=True,string="record valid check")

    # @api.model
    # def default_get(self, fields):
    #     '''
    #     :param fields:
    #     :return:
    #     '''
    #     res = super(KdItemLine, self).default_get(fields)
    #     res.update({'state': 'ready'})
    #
    #     return res

    # def _valid_check(self):
    #     pass

    @api.onchange('char_value','text_value','image_value','date_value','time_value','list_value','boolean_value', \
                  'integer_value','float_value')
    def _chck_validation(self):
        record_name = self.name
        if self.char_type == True:
            if self.is_mandatory == True:
                if (self.char_value == False):
                    raise ValidationError(_('Error: Record '+record_name+'[{}] is a record that must be entered.'.format('char')))
        elif self.text_type == True:
            if self.is_mandatory == True:
                if (self.text_value == False):
                    raise ValidationError(_('Error: Record '+record_name+'[{}] is a record that must be entered.'.format('text')))
        elif self.image_type == True:
            if self.is_mandatory == True:
                if (self.image_value == None):
                    raise ValidationError(_('Error: Record '+record_name+'[{}] is a record that must be entered.'.format('image')))
        elif self.date_type == True:
            if self.is_mandatory == True:
                if (self.date_value == False):
                    raise ValidationError(_('Error: Record '+record_name+'[{}] is a record that must be entered.'.format('date')))
        elif self.time_type == True:
            if self.is_mandatory == True:
                if (self.time_value == False):
                    raise ValidationError(_('Error: Record '+record_name+'[{}] is a record that must be entered.'.format('time')))
                else:
                    try:
                        datetime.strptime(self.time_value, '%H:%M')
                    except:
                        raise ValidationError(
                            _('Error: Record ' + record_name + '[{}] is a record that must be entered.'.format('time')))
        elif self.list_type == True:
            if self.is_mandatory == True:
                if self.datalist_id['name'] == False:
                    raise ValidationError(_('Error: Record '+record_name+'[{}] is Incorrect list value'.format('list')))
        elif self.boolean_type == True:
            pass # 기본 값이 False 또는 True
        elif self.integer_type == True:
            if self.integer_value > self.maximum_value:
                raise ValidationError(_('Error: Record ' + record_name + '[{}] is Incorrect Maximum value'.format(str('integer'))))
            if self.integer_value < self.minimum_value:
                raise ValidationError(_('Error: Record ' + record_name + '[{}] is Incorrect Minimum value'.format('integer')))
        elif self.float_type == True:
            if self.float_value > self.maximum_value:
                raise ValidationError(_('Error: Record ' + record_name + '[{}] is Incorrect Maximum value'.format('float')))
            if  self.float_value < self.minimum_value:
                raise ValidationError(_('Error: Record ' + record_name + '[{}] is Incorrect Minimum value'.format('float')))

    def current_item(self):
        return str('10')

    @api.multi
    def write(self, vals):
        itemSourceSchema = ['is_mandatory', 'data_type', 'default_value', 'datalist_id','maximum_value','minimum_value']

        domain_item = [('id', '=', self.item_id.id)]
        itemSource = self.env['kd.item'].sudo().search_read(domain_item, fields=itemSourceSchema)

        if 'integer_value' in vals:

            try:
                tmp = int(vals['integer_value'])
            except Exception as e:
                raise ValidationError(_('Error: The value entered is not an integer value.', e))

            if vals['integer_value'] > itemSource[0]['maximum_value']:
                raise ValidationError(_('Error: Maximum[{}] possible value error'.format(str(itemSource[0]['maximum_value']))))
            if vals['integer_value'] < itemSource[0]['minimum_value']:
                raise ValidationError(_('Error: Minimum[{}] possible value error'.format(str(itemSource[0]['minimum_value']))))

        if 'float_value' in vals:
            # 최소 입력은 0.01 까지 이다.
            try:
                tmp = int(vals['float_value'])
            except Exception as e:
                raise ValidationError(_('Error: The value entered is not an float value.', e))

            if vals['float_value'] > itemSource[0]['maximum_value']:
                raise ValidationError(_('Error: Maximum[{}] possible value error'.format(str(itemSource[0]['maximum_value']))))
            if vals['float_value'] < 0.01:
                raise ValidationError(_('Error: Minimum[{}] possible value error'.format('0.01')))

        if 'char_value' in vals:
            if self.data_size > 0:
                trim_char = vals['char_value'][0:self.data_size]
                vals['char_value'] = trim_char

        if 'text_value' in vals:
            if self.data_size > 0:
                trim_char = vals['char_value'][0:self.data_size]
                vals['char_value'] = trim_char

        return super(KdItemLine, self).write(vals)
