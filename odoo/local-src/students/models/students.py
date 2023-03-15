from odoo import fields, models, api
from odoo.exceptions import ValidationError


class StudentsTraining(models.Model):
    _name = "students.training"
    _description = "Training table"
    _rec_name = "code"

    code = fields.Char(string="Training code", size=4, required=True)
    name = fields.Char(string="Training name", size=100, required=True)
    student_ids = fields.One2many(
        string="Training students",
        comodel_name="students.student",
        inverse_name="training_id",
    )

    @api.constrains('code')
    def _check_code_uniqueness(self):
        for record in self:
            existing_training = self.env['students.training'].search(
                [('code', '=', record.code), ('id', '!=', record.id)])
            if existing_training:
                raise ValidationError("Training code must be unique!")


class StudentsStudent(models.Model):
    _name = "students.student"
    _description = "Student table"
    _rec_name = "number"

    number = fields.Char("Student number", size=11, required=True)
    firstname = fields.Char("Student firstname", size=64, required=True)
    lastname = fields.Char("Student lastname", size=64, required=True)
    mark_ids = fields.One2many('students.mark', 'student_id', string="Marks")
    weighted_average = fields.Float(string="Weighted Average", compute='_compute_weighted_average', readonly=True)

    nationalite_id = fields.Many2one(
        string="Country",
        comodel_name="res.country",
        ondelete="cascade",
    )

    training_id = fields.Many2one(
        string="Training",
        comodel_name="students.training",
        ondelete="cascade",
    )

    mark_ids = fields.One2many(
        string="Mark students",
        comodel_name="students.mark",
        inverse_name="student_id",
    )

    weighted_average = fields.Float(
        string="Grade point average",
        compute="_compute_weighted_average",

    )

    def name_get(self):
        result = []
        for record in self:
            name = record.firstname + " " + record.lastname
            result.append((record.id, name))
        return result

    @api.depends('mark_ids')
    def _compute_weighted_average(self):
        for record in self:
            total_marks = 0
            total_weight = 0
            record.weighted_average = 0
            if record.mark_ids:
                for mark in record.mark_ids:
                    total_marks += mark.mark * int(mark.coefficient)
                    total_weight += int(mark.coefficient)
                if total_weight > 0:
                    record.weighted_average = (total_marks / total_weight)
                else:
                    record.weighted_average = 0.0


class StudentsMark(models.Model):
    _name = 'students.mark'

    student_id = fields.Many2one('students.student', string="Student")
    mark = fields.Float(string="Mark")
    coefficient = fields.Float(string="Coefficient")

    @api.constrains('name')
    def _check_note_range(self):
        for record in self:
            if record.name < 0 or record.name > 20:
                raise ValidationError("Note must be between 0 and 20.")

    def name_get(self):
        res = []
        for record in self:
            name = record.firstname + ' ' + record.lastname
            res.append((record.id, name))
        return res

    @api.depends("mark_ids")
    def _compute_weighted_average(self):
        for record in self:
            total_weighted_marks = 0
            total_coefficients = 0
            for mark in record.mark_ids:
                total_weighted_marks += mark.mark * int(mark.coefficient)
                total_coefficients += int(mark.coefficient)
            if total_coefficients > 0:
                record.weighted_average = (total_weighted_marks / total_coefficients)
            else:
                record.weighted_average = 0


class StudentsStudentContinuous(models.Model):
    _name = "students.studentcontinuous"
    _inherit = 'students.student'
    _description = "Student table"

    partner_id = fields.Many2one(
        string="Partner",
        comodel_name="res.partner",
        ondelete="cascade",
    )


class StudentMark(models.Model):
    _name = "students.mark"
    _description = "Mark table"

    coefficient = fields.Selection([
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('5', '5'),
    ], string='Coefficient', required=True, default='1', index=True, help="Select a coefficient in the list")
    subject = fields.Char("Mark subject", size=64, required=True)
    mark = fields.Integer("Mark Mark", required=True)
    student_id = fields.Many2one(
        string="Student",
        comodel_name="students.student",
        ondelete="cascade",
    )

    weightedMark = fields.Float(
        string="Weighted Mark",
        compute="_compute_mark_coefficiented",
    )

    @api.constrains('mark')
    def _check_mark_range(self):
        for record in self:
            if record.mark < 0 or record.mark > 20:
                raise models.ValidationError("The mark should be between 0 and 20!")

    @api.onchange("mark", "coefficient")
    def _compute_mark_coefficiented(self):
        for record in self:
            record.weightedMark = record.mark * float(record.coefficient)
