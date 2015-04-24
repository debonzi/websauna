import deform
import deform.widget as w
import colander as c


from hem.schemas import CSRFSchema
from horus.schemas import unique_email

PASSWORD_MIN_LENGTH = 6


class RegisterSchema(CSRFSchema):
    """Username-less registration form schema."""

    email = c.SchemaNode(
        c.String(),
        title='Email',
        validator=c.All(c.Email(), unique_email),
        widget=w.TextInputWidget(size=40, maxlength=260, type='email'))

    password = c.SchemaNode(
        c.String(),
        validator=c.Length(min=PASSWORD_MIN_LENGTH),
        widget=deform.widget.CheckedPasswordWidget(),
    )


class LoginSchema(CSRFSchema):
    """Login form schema.

    The user can log in both with email and his/her username, though we recommend using emails as users tend to forget their usernames.
    """

    username = c.SchemaNode(c.String(), title='Email', validator=c.All(c.Email()), widget=w.TextInputWidget(size=40, maxlength=260, type='email'))

    password = c.SchemaNode(c.String(), widget=deform.widget.PasswordWidget())



class ResetPasswordSchema(CSRFSchema):
    user = c.SchemaNode(
        c.String(),
        missing=c.null,
        widget=deform.widget.TextInputWidget(template='readonly/textinput'))

    password = c.SchemaNode(
        c.String(),
        validator=c.Length(min=2),
        widget=deform.widget.CheckedPasswordWidget()
    )
