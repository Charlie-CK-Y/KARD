# -*- coding: utf-8 -*-
from datetime import datetime as dt
from odoo import models, fields, api,_
from odoo.exceptions import ValidationError

"""
1. Research Model Referenced Core Module 
2. Case Model Referenced Media
3. The inspection request model refers to the media unit model.
4. The inspection request model refers to the media movement.
"""

adminLoginID = 'kard'


class KdCase(models.Model):
    _name = 'kd.case'
    _rec_name = 'name'
    _inherit = 'mail.thread'

    name = fields.Char('Case Name')
    create_uid = fields.Many2one('res.users', default=lambda self: self.env.user and self.env.user.id or False, \
                                 readonly=True, string='Create User')
    tags = fields.Many2many('op.tag', string='Tag(s)')
    description = fields.Text('Description')
    state = fields.Selection([('preparing', 'Preparing'),('available', 'Available'), ('issue', 'Issued')],'State', default='preparing', track_visibility='onchange')
    istemplate = fields.Boolean('template', default=False)
    # 관리자와 사용자의 Template 읽기 권한 적용
    is_template_readonly = fields.Boolean('Template Read Allow',default=False,compute='_get_is_approver', track_visibility='onchange')
    isclose = fields.Boolean(default=False, string="Completed", compute="_is_item_allclose", stored=True)
    # Case에서 VisitSet 생성 이후 중복 생성 방지용
    isVisitCreated = fields.Boolean('visitset lock',default=False,help='Check to lock the automatic generation of the visit template (it is automatically locked after creation).')
    help = fields.Html('Help')

    # One2Many
    visit_ids = fields.One2many('kd.visit','case_id','Case Visit(s)')

    # Many2One
    case_worker_ids = fields.Many2one('kd.worker',string='Related researcher(s)')
    research_id = fields.Many2one('kd.research',string='Research Name',required=True)
    visitset_id = fields.Many2one('kd.visitset',string='Visit Set')


    # _sql_constraints = [
    #     ('unique_name_case',
    #      'unique(case_code)',
    #      'Case Code must be unique per case!'),
    #     ('unique_name_internal_code',
    #      'unique(internal_code)',
    #      'Internal Code must be unique per case!'),
    # ]
    # @api.model
    # def create(self, vals):
    #     x = self.env['ir.sequence'].next_by_fields_view_getcode('kd.case')
    #     vals['name'] = 'case title # {}'.format(str(x))
    #     return super(KdCase, self).create(vals)

    @api.model
    def default_get(self, fields):
        '''
        생성 후 기본 값 설정하기.
        일괄 생성시에는 사용하면 안됨.
        :param fields:
        :return:
        '''
        res = super(KdCase, self).default_get(fields)
        # active_id = self.env.context.get('active_id', False)
        # defaultVisitSet = self.env['kd.visitset'].browse(active_id)
        domainDefaultVisitSet = [('state', '=', 'available')]
        domainVisitSet = [('state', '=', 'available'), ('isdefault', '=', True)]

        domainCaseCount = [('create_uid','=',self._uid)]

        CaseCount = self.env['kd.case'].search_count(domainCaseCount)

        domain_research = [('state', '=', 'available')]
        researchName = self.env['kd.research'].sudo().search_read(domain_research,limit=1,order="id desc")

        if not researchName:
            raise ValidationError(_('Error: Research is not selected.'))

        if CaseCount == 0:
            CaseCount = 1

        if researchName:
            res.update({'name': researchName[0]['research_title']+'-'+str(self.env.user.name)+'-#'+str(CaseCount)})
        else:
            res.update({'name': 'Unselected research-'+str(self.env.user.name)+'-#'+str(CaseCount)})

        siteDefaultVisitSet = self.env['kd.visitset'].sudo().search_read(domainDefaultVisitSet, ['visitset_id'])

        if siteDefaultVisitSet:
            defaultVisitSet = self.env['kd.visitset'].sudo().search_read(domainVisitSet, ['id'])
        else:
            raise ValidationError(_('Error: vistset does not exist'))

        if defaultVisitSet:
            res.update({'visitset_id': defaultVisitSet[0]['id']})

        return res

    @api.one
    def _get_is_approver(self):
        '''
        템플릿 사용 권한 확인.
        :return:
        '''
        approver_group = self.env.ref('openkard_research.group_kd_visit_template_admin')

        users = approver_group.users

        for user in users:
            if user.id == self._uid:
                self.is_template_readonly = True
                return

        self.is_template_readonly = False

    @api.one
    def _is_item_allclose(self):
        allclose = False
        for visit in self.visit_ids:
            domain_visit = [('isclose', '=', True), ('id', '=', visit[0]['id'])]
            visitCheck = self.env['kd.visit'].sudo().search_read(domain_visit, fields=['isclose'])
            if visitCheck:
                allclose = visitCheck[0]['isclose']
            else:
                allclose = False
                break

        if allclose == True:
            self.isclose = True
        else:
            self.isclose = False

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

        return super(KdCase, self).write(vals)

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

        res = super(KdCase, self).unlink()
        return res

    @api.multi
    def open_case_view(self):
        return {
            'name':('act_open_kd_visit_view_form'),
            'type': 'ir.actions.act_window',
            'view_type':'form',
            'view_mode': 'form',
            'res_model': 'kd.case',
            'target': 'current',
            'res_id': self.id
        }

    @api.multi
    def create_vistset(self,research_id):
        '''
        VisitSet 생성하기(Visit, ItemSet)
        :return:
        '''

        if self.env.user.id != self.create_uid.id:
            raise ValidationError(_('Error: You are not the author of this document. Check your user rights.'))

        domainVisitCount = [('create_uid', '=', self._uid),('case_id','=',self.id)]
        visitCount = self.env['kd.visit'].search_count(domainVisitCount)
        resultCount = 0

        if not self.sudo().visitset_id.visitset_line_ids:
            raise ValidationError(_('Error: Visit Template is not linked to VisitSet.'))

        domainVistSet = [('research_id', '=', self.research_id.id), ('isdefault', '=', True),('state', '=', 'available')]
        visitset_by_name  = self.env['kd.visitset'].sudo().search_read(domainVistSet, ['visitset_line_ids'])
        # i = 0

        for visit in self.sudo().visitset_id.visitset_line_ids:
            try:

                # self.env.cr.commit()

                # 1. Case에 설정된 VistSet(Visit Template)의 Vist
                if visit.visit_id:

                    domaTemplateVist = [('id', '=', visit.visit_id.id)]
                    templateVisitName = self.env['kd.visit'].sudo().search_read(domaTemplateVist,['name'])

                    # domainVistSet = [('research_id', '=', self.research_id.id),('isdefault','=',True),('state','=','available')]
                    # visitsetName = self.env['kd.visitset'].sudo().search_read(domainVistSet, ['name'])

                    # domainVistSetName = [('id', '=', visitset_by_name[0]['visitset_line_ids'][i])]
                    # visitsetName = self.env['kd.visit'].sudo().search_read(domainVistSetName, ['name'])
                    # i = i + 1


                    if templateVisitName == False:
                        raise ValidationError(_('Error: VisitSet is not found.'))

                    visitCount = visitCount + 1

                    visitName = '{}-{}'.format(self.name,templateVisitName[0]['name'])

                    newVisit = self.visit_ids.create({'name': visitName, \
                                                      'state': 'available', \
                                                      'create_uid': self.create_uid, \
                                                      'case_id': self.id})

                    resultCount = resultCount + 1

                    resultName = 'RESULT-{}-{}'.format(str(self.env.user.name), str(resultCount))

                    # Result에서 template 이면서 visit_id가 visit템플릿과 동일한 자료에서 ItemSetID를 가져 온다.
                    domain_result = [('istemplate', '=', 't'), ('visit_id', '=', visit.visit_id['id'])]
                    visitSetItemSetID = self.env['kd.result'].sudo().search_read(domain_result, fields=['itemset_id','name'])

                    # newVisit.name = newVisit.name+'-'+visitSetItemSetID[0]['itemset_id'][1]

                    newResult = newVisit.result_lines.create({'name':resultName, \
                                                              'visit_id': newVisit.id, \
                                                              'state': 'available', \
                                                              'create_uid':self.create_uid, \
                                                              'isautocreated':True,
                                                              'itemset_id': visitSetItemSetID[0]['itemset_id'][0]})

                    # todo-18.05.26 하위 품목까지 자동 생성-Completed(05.26)
                    # Result에 넣어준 ItemSet ID로 ItemSet에서 Item 목록을 가져와 item_line에 넣어 준다.
                    domain_itemlist = [('itemset_id', '=',visitSetItemSetID[0]['itemset_id'][0] )]
                    itemSourceList = self.env['kd.itemset.line'].sudo().search_read(domain_itemlist, fields=['item_id'])

                    for item in itemSourceList:
                        domain_item = [('id', '=', item['item_id'][0])]
                        itemType = self.env['kd.item'].sudo().search_read(domain_item,fields=['data_type','default_value','datalist_id'])

                        iType = itemType[0]['data_type']

                        if itemType:
                            default_value = itemType[0]['default_value']
                        else:
                            default_value = '0'

                        if iType == 'selection':
                            domain_item_datalist = [('id', '=', itemType[0]['datalist_id'][0])]
                            itemDataDefault = self.env['kd.datalist'].sudo().search_read(domain_item_datalist,fields=['default_value'])
                            default_value = itemDataDefault[0]['default_value']

                        if iType =='integer':
                            try:
                                integer_value = int(default_value)
                            except:
                                integer_value = 0
                            newResult.item_ids.create({'result_id': newResult.id, \
                                                       'item_id': item['item_id'][0], \
                                                       'create_uid': self.create_uid, \
                                                       'integer_type':True,
                                                       'integer_value': integer_value})
                        elif iType =='float':
                            try:
                                float_value = float(default_value)
                            except:
                                float_value = 0.0
                            newResult.item_ids.create({'result_id': newResult.id, \
                                                       'item_id': item['item_id'][0], \
                                                       'create_uid': self.create_uid, \
                                                       'float_type': True, \
                                                       'float_value': float_value})
                        elif iType =='char':
                            newResult.item_ids.create({'result_id': newResult.id, \
                                                       'item_id': item['item_id'][0], \
                                                       'create_uid': self.create_uid, \
                                                       'char_type': True, \
                                                       'char_value': default_value})
                        elif iType =='text':
                            newResult.item_ids.create({'result_id': newResult.id, \
                                                       'item_id': item['item_id'][0], \
                                                       'create_uid': self.create_uid, \
                                                       'text_type': True, \
                                                       'text_value' : default_value})
                        elif iType =='date':
                            try:
                                date_value = dt.strftime(dt.strptime(default_value, "%m-%d-%Y"),"%m-%d-%Y")
                            except:
                                date_value = dt.now()

                            newResult.item_ids.create({'result_id': newResult.id, \
                                                       'item_id': item['item_id'][0], \
                                                       'create_uid': self.create_uid, \
                                                       'date_type': True, \
                                                       'date_value': date_value})
                        elif iType =='time':
                            newResult.item_ids.create({'result_id': newResult.id, \
                                                       'item_id': item['item_id'][0], \
                                                       'create_uid': self.create_uid, \
                                                       'time_type': True, \
                                                       'time_value': default_value})
                        elif iType =='selection':
                            datalist = self.env['kd.datalist'].sudo().search_read([('id', '=', itemType[0]['datalist_id'][0])], \
                                                                                  fields=['name', 'default_value','item_id','title'])
                            if datalist:
                                # 결과의 데이터 목록
                                # todo - 오류 케이스 생성시 목록 오류 발생
                                resultDataList = self.env['kd.item.line.datalist'].sudo().search_read([('item_id', '=', itemType[0]['id'])], fields=['name', 'value'])

                                # 없으면 만들어 준다.
                                defaultId ='n/a'
                                defaultValue = 'n/a'
                                for listvalue in datalist[0]['name'].split(','):

                                    if not resultDataList:
                                        self.env['kd.item.line.datalist'].create({'name':listvalue, \
                                                                                  'title':datalist[0]['title'], \
                                                                                  'create_uid': self.create_uid, \
                                                                                  'value':listvalue,
                                                                                  'item_id':itemType[0]['id']})

                                    resultDataList = self.env['kd.result.datalist'].sudo().search_read(
                                        [('name', '=', listvalue)])

                                    if not resultDataList:
                                        self.env['kd.result.datalist'].create({'title':datalist[0]['title'],
                                                                               'name': listvalue, \
                                                                               'value': listvalue,
                                                                               'resultIds':newResult})

                                # 추가 후 다시 검색 해 가져온다.
                                itemDataList = self.env['kd.item.line.datalist'].sudo().search_read([('item_id', '=', itemType[0]['id'])], fields=['name', 'value'])
                                # itemDataList = self.env['kd.result.datalist'].sudo().search_read([('item_id', '=', itemType[0]['id'])], fields=['name', 'value'])

                                for itemData in itemDataList:
                                    if itemData['value'] == default_value:
                                        defaultId = itemData['id']
                                        defaultValue = itemData['value']

                                if (default_value != 'n/a') and (default_value != '0') and (default_value != False):
                                    # 디폴트 선택 값으로 설정
                                    newResult.item_ids.create({'result_id': newResult.id, \
                                                               'item_id': item['item_id'][0], \
                                                               'create_uid': self.create_uid, \
                                                               'list_type': True, \
                                                               'datalist_id':defaultId, \
                                                               'list_value': default_value})
                                else:
                                    newResult.item_ids.create({'result_id': newResult.id, \
                                                               'item_id': item['item_id'][0], \
                                                               'create_uid': self.create_uid, \
                                                               'list_type': True, \
                                                               'datalist_id': 0, \
                                                               'list_value': ''})

                            else:
                                newResult.item_ids.create({'result_id': newResult.id, \
                                                           'item_id': item['item_id'][0], \
                                                           'create_uid': self.create_uid, \
                                                           'list_type': True})
                        elif iType =='boolean':
                            if default_value == 'True':
                                boolean_value = True
                            else:
                                boolean_value = False

                            newResult.item_ids.create({'result_id': newResult.id, \
                                                       'item_id': item['item_id'][0], \
                                                       'create_uid': self.create_uid, \
                                                       'boolean_type': True, \
                                                       'boolean_value': int(boolean_value)})
                        elif iType =='image':
                            newResult.item_ids.create({'result_id': newResult.id, \
                                                       'item_id': item['item_id'][0], \
                                                       'create_uid': self.create_uid, \
                                                       'image_type': True})


                else:
                    pass

            except Exception as e:
                print e
        # 일괄 생성 후 중복 생성 방지를 위해 설정
        self.isVisitCreated = True

        self.refresh
