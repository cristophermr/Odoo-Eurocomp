from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    eurocomp_username = fields.Char(string='Eurocomp username', help="Eurocomp username")
    eurocomp_password = fields.Char(string='Eurocomp password', help="Eurocomp password")
    eurocomp_stock_min = fields.Integer(string='Stock Mimimun on system', help="Eurocomp stock min")
    eurocomp_margin = fields.Integer(string='Profit margin', help="Profit margin of imported products")


    @api.model
    def get_values(self):
        res = super(ResConfigSettings,self).get_values()
        get_param = self.env['ir.config_parameter'].sudo().get_param
        try:
            eurocomp_username = get_param('eurocomp_username') if get_param('eurocomp_username') else False
            eurocomp_password = get_param('eurocomp_password') if get_param('eurocomp_password') else False
            eurocomp_stock_min = get_param('eurocomp_stock_min') if get_param('eurocomp_stock_min') else False
            eurocomp_margin = get_param('eurocomp_margin') if get_param('eurocomp_margin') else False
        except (TypeError, ValueError):
            eurocomp_username = False
            eurocomp_password = False
            eurocomp_stock_min = False
            eurocomp_margin = False

        res.update(
            eurocomp_username=eurocomp_username,
            eurocomp_password=eurocomp_password,
            eurocomp_stock_min=eurocomp_stock_min,
            eurocomp_margin=eurocomp_margin
        )
        return res

    @api.model
    def set_values(self):
        super(ResConfigSettings,self).set_values()
        set_param = self.env['ir.config_parameter'].sudo().set_param

        if self.eurocomp_username:
            set_param('eurocomp_username', self.eurocomp_username)
        if self.eurocomp_password:
            set_param('eurocomp_password', self.eurocomp_password)
        if self.eurocomp_stock_min:
            set_param('eurocomp_stock_min', self.eurocomp_stock_min)
        if self.eurocomp_margin:
            set_param('eurocomp_margin', self.eurocomp_margin)
