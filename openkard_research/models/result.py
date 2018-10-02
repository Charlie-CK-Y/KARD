# -*- coding: utf-8 -*-

"""
1. Research Model Referenced Core Module
2. Case Model Referenced Media
3. The inspection request model refers to the media unit model.
4. The inspection request model refers to the media movement.
"""

from odoo import models, fields, api,_
from odoo.exceptions import ValidationError

adminLoginID ='kard'

class KdInspectResult(models.Model):
    '''
    Visit와 1:1로 매칭되어 결과를 입력 받음, 하위에는 Item에서 상속받은 Item.line를 통해 result_id,item_id로 관리 함.
    '''
    _name = 'kd.result'
    _rec_name = 'name'
    _inherit = 'mail.thread'
    _description = 'Case Inspection Result'

    name = fields.Char('Name',releated=id)
    create_uid = fields.Many2one('res.users', default=lambda self: self.env.user and self.env.user.id or False,
                                 readonly=True, string='Create User')
    state = fields.Selection([('available', 'Available'), ('issue', 'Issued')],'State', \
                             default='available', track_visibility='onchange')
    istemplate = fields.Boolean('template', default=False)
    is_template_readonly = fields.Boolean('Template Readonly', default=False, compute='_get_template_group')

    # Many2one
    visit_id = fields.Many2one('kd.visit', 'Visit ID', required=True, track_visibility='onchange')
    itemset_id = fields.Many2one('kd.itemset','Item Set')
    datalist_id = fields.Many2one('kd.result.datalist', '항목 목록' ,ondelete='cascade')

    isautocreated = fields.Boolean('itemset lock', default=False, \
                                    help='Check to lock the automatic generation of the item template (it is automatically locked after creation).')

    item_ids = fields.One2many('kd.item.line', 'result_id', 'Result item(s)')
    isclose = fields.Boolean(default=False, string="Completed",compute="_is_item_allclose", stored=True)

    # _sql_constraints = [
    #     ('unique_name_result_code',
    #      'unique(result_code)',
    #      'Result Code must be unique per Case Inseception!'),
    # ]

    # @api.model
    # def default_get(self, fields):
    #
    #     res = super(KdInspectResult, self).default_get(fields)
    #
    #     if self.visit_id.id == False:
    #         domainResultCount = [('create_uid', '=', self._uid)]
    #     else:
    #         domainResultCount = [('visit_id', '=', self.visit_id)]
    #
    #     ResultCount = self.env['kd.result'].search_count(domainResultCount)
    #
    #     res.update({'name': 'RESULT-{}-{}'.format(str(self.env.user.id), str(ResultCount))})
    #
    #     return res

    @api.model
    def _get_template_group(self):
        '''
        생성 후 기본 값 설정하기.
        일괄 생성시에는 사용하면 안됨.
        :param fields:
        :return:
        '''

        groupId = self.env.user.groups_id[0]['id']
        domainAdminGroup = [('id', '=', groupId)]

        AdminGroup = self.env['res.groups'].search_read(domainAdminGroup, ['full_name'])

        if (AdminGroup[0]['full_name'] == 'OpenKard Core / Researcher') or \
                (AdminGroup[0]['full_name'] == 'Administration / Access Rights'):
            self.is_template_readonly = True
        else:
            self.is_template_readonly = False

    @api.model
    def create(self, vals):

        istemplate = False
        for tmp in vals:
            if tmp == 'istemplate':
                istemplate = True

        if istemplate == True:

            if vals['visit_id'] == False:
                raise ValueError("please select visit id")
            else:
                domainResultCount = [('id', '=', vals['visit_id'])]

            ResultCount = self.env['kd.visit'].search_count(domainResultCount)

            vals['name'] = 'RESULT-{}-{}'.format(str(self.env.user.name), str(ResultCount))

        return super(KdInspectResult, self).create(vals)

    @api.multi
    def write(self, vals):
        if self.env.user.id != self.create_uid.id:
            domain_admin = [('login', '=', adminLoginID)]
            adminId = self.env['res.users'].sudo().search_read(domain_admin, fields='id')
            if self.env.user.id == adminId[0]['id']:
                pass  # 관리자 인 경우인 경우 삭제 가능
            elif self.env.user.id == self.create_uid[0]['id']:
                pass  # 작성자 와 동일한 경우 삭제 가능
            else:
                raise ValidationError(_('Error: You are not the author of this document. Check your user rights.'))

        return super(KdInspectResult, self).write(vals)

    @api.multi
    def unlink(self):
        domain_admin = [('login', '=', adminLoginID)]
        adminId = self.env['res.users'].sudo().search_read(domain_admin, fields='id')
        if self.env.user.id == adminId[0]['id']:
            pass  # 관리자 인 경우인 경우 삭제 가능
        elif self.env.user.id == self.create_uid[0]['id']:
            pass  # 작성자 와 동일한 경우 삭제 가능
        else:
            raise ValidationError(_('Error: You are not the author of this document. Check your user rights.'))

        res = super(KdInspectResult, self).unlink()
        return res

    # @api.model
    # def name_search(self, name, args=None, operator='ilike', limit=100):
    #     args = args or []
    #     recs = self.browse()
    #     if name:
    #         recs = self.search(
    #             [('name', operator, name)] + args, limit=limit)
    #     if not recs:
    #         recs = self.search(
    #             [('result_code', operator, name)] + args, limit=limit)
    #     return recs.name_get()

    @api.one
    def newitemset(self):
        '''
        결과에서 사용할 IitemSet로 ItemSet에 연결된 Item 소스를 사용해 Result에서 사용할 결과지 용 Item을 Item_ids에 복사 해준다.
        :return:
        '''
        if self.env.user.id != self.create_uid.id:
            raise ValidationError(_('Error: You are not the author of this document. Check your user rights.'))

        for item in self.itemset_id.itemset_line_ids:
            if self.istemplate:
                self.item_ids.create({'item_id':item.item_id.id, 'result_id': self.id,'istemplate':True})
            else:
                self.item_ids.create({'item_id': item.item_id.id, 'result_id': self.id})

        self.isautocreated = True

        self.refresh

    @api.one
    def _is_item_allclose(self):
        allclose = False
        for item in self.item_ids:
            domain_admin = [('isclose', '=', True),('id','=',item[0]['id'])]
            itemCheck = self.env['kd.item.line'].sudo().search_read(domain_admin, fields=['isclose'])
            if itemCheck:
                allclose = itemCheck[0]['isclose']
            else:
                allclose = False
                break

        if allclose == True:
            self.isclose = True
        else:
            self.isclose = False

        return allclose


class KardResultDatalist(models.Model):
    _name = 'kd.result.datalist'
    _description = 'result selection list'
    _rec_name = 'name'

    title = fields.Char(string='목록 제목')
    name = fields.Text(string='목록 데이터',default='예)서울,부산,대구')
    value = fields.Char(string='결과코드',default='n/a')

    # 다른 쪽을 참조하고 있는 테이블
    # 사용하는쪽_이름+s = fields.One2many('참조하는쪽','사용하는쪽_id','사용하는이름(s)'
    resultIds = fields.One2many('kd.result','datalist_id', '답변 목록')
