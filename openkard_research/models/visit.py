# -*- coding: utf-8 -*-

"""
1. Research Model Referenced Core Module
2. Case Model Referenced Media
3. The inspection request model refers to the media unit model.
4. The inspection request model refers to the media movement.
"""
from datetime import datetime
from odoo import models, fields, api,_
from odoo.exceptions import ValidationError

adminLoginID = 'kard'

class KdResearchVist(models.Model):
    _name = 'kd.visit'
    _rec_name = 'name'
    _inherit = 'mail.thread'
    _description = 'openkard visit model'

    name = fields.Char('Vist Name',default='visit_name')

    create_uid = fields.Many2one('res.users',default=lambda self: self.env.user and self.env.user.id or False, readonly=True,string='Create User')
    state = fields.Selection([('preparing', 'Preparing'), ('available', 'Available'), ('issue', 'Issued')], 'State', \
                             default='preparing', track_visibility='onchange')
    curr_visit_date = fields.Date('Visit date',default=datetime.today())
    istemplate = fields.Boolean('template',default=False)
    is_template_readonly = fields.Boolean('Template Readonly',default=False,compute='_get_template_group')
    isclose = fields.Boolean(default=False, string="Completed", compute="_is_item_allclose", stored=True)

    # One2Many
    result_lines = fields.One2many('kd.result','visit_id','Visit Results')


    # Many2one
    case_id = fields.Many2one('kd.case', 'Case Name', required=True)


    # _sql_constraints = [
    #     ('unique_name_visit_code',
    #      'unique(visit_code)',
    #      'visit Code must be unique per Research Case!'),
    # ]

    # @api.model
    # def default_get(self, fields):
    #     res = super(KdResearchVist, self).default_get(fields)
    #
    #     if self.case_id.id == False:
    #         domainVisitCount = [('create_uid','=',self._uid)]
    #     else:
    #         domainVisitCount = [('case_id', '=', self.case_id)]
    #
    #     VisitCount = self.env['kd.visit'].search_count(domainVisitCount)
    #
    #     res.update({'name': 'VISIT-{}-{}'.format(str(self.env.user.id), str(VisitCount))})
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

        if (AdminGroup[0]['full_name'] =='OpenKard Core / Researcher') or \
                (AdminGroup[0]['full_name'] == 'Administration / Access Rights'):
            self.is_template_readonly = True
        else:
            self.is_template_readonly = False

    @api.model
    def create(self, vals):
        # Visit 템플릿을 따로 만들떄와 일괄(일반사용자)생성할 때 문제로 인해 default_get을 사용하지 않는다.
        # 템플릿인 경우에만 Visit Name를 생성 해준다.

        istemplate = False
        for tmp in vals:
            if tmp== 'istemplate':
                istemplate = True

        if istemplate == True:
            if self.case_id.id == False:
                domainVisitCount = [('create_uid','=',self._uid)]
            else:
                domainVisitCount = [('case_id', '=', self.case_id)]

            VisitCount = self.env['kd.visit'].search_count(domainVisitCount)

            vals['name'] = 'VISIT-{}-{}'.format(str(self.env.user.name), str(VisitCount))

        return super(KdResearchVist, self).create(vals)

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



        return super(KdResearchVist, self).write(vals)

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

        res = super(KdResearchVist, self).unlink()
        return res

    @api.one
    def _is_item_allclose(self):
        allclose = False
        for result in self.result_lines:
            domain_result = [('isclose', '=', True),('id','=',result[0]['id'])]
            resultCheck = self.env['kd.result'].sudo().search_read(domain_result, fields=['isclose'])
            if resultCheck:
                allclose = resultCheck[0]['isclose']
            else:
                allclose = False
                break

        if allclose == True:
            self.isclose = True
        else:
            self.isclose = False

        return allclose

    class KDVisitLine(models.Model):
        _name = 'kd.visit.line'
        _rec_name = 'visit_id'

        visit_id = fields.Many2one('kd.visit','방문', required=True)

    @api.multi
    def update_visit_result(self):

        res = self.env['ir.model.data'].get_object_reference('openkard_research', 'act_open_kd_result_view_form')
        res_id = res and res[1] or False

        visit_Obj = self.env['kd.visit']
        selectVisit = visit_Obj.browse(self.id)
        visit_result_id = selectVisit.result_lines[0].id

        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'kd.result',
            'target': 'new',
            'res_id': visit_result_id
        }

    @api.multi
    def open_visit_result(self):

        res = self.env['ir.model.data'].get_object_reference('openkard_research', 'act_open_kd_result_view_form')
        res_id = res and res[1] or False

        visit_Obj = self.env['kd.visit']
        selectVisit = visit_Obj.browse(self.id)
        visit_result_id = selectVisit.result_lines[0].id

        return {
            'name':('act_open_kd_result_view_form'),
            'type': 'ir.actions.act_window',
            'view_type':'form',
            'view_mode': 'form',
            'res_model': 'kd.result',
            'target': 'current',
            'res_id': visit_result_id
        }

    # def show_ru_assignments_sub_view(self, cr, uid, ids, context=None):
    #     return {
    #         'name': ('Assignment Sub'),
    #         'view_type': 'form',
    #         'view_mode': 'form',
    #         'res_model': 'ru.assignments.sub',
    #         'view_id': False,
    #         'type': 'ir.actions.act_window',
    #         'target': 'new'
    #     }

    # @api.model
    # def name_search(self, name, args=None, operator='ilike', limit=100):
    #     args = args or []
    #     recs = self.browse()
    #     if name:
    #         recs = self.search(
    #             [('name', operator, name)] + args, limit=limit)
    #     # if not recs:
    #     #     recs = self.search(
    #     #         [('visit_code', operator, name)] + args, limit=limit)
    #     return recs.name_get()
