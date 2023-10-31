# Design choices

## Roles

We identified 3 roles

- Admin: Can provision users
    - ERP using the super secret key
- Staff: Can hijack users
    - TOVALIDATE: res.user?
- Customer: Plain users
    - Customer valid res_partner with the `customer` category.


## Authentication

As we use emails and nifs as login, and nifs can be vats for foreigners,
we decided to split those 3 concepts for params and variable names,
to explicit the semantics of a variable.

- Login: Whatever users uses to identify themselves: They may use a NIF, a VAT or a email (whichever the role)
    - allow email login for customers: to allow user google account until we have the auth server
- Username: What the OV uses to identify a user:
    - VAT for customers (even spanish, removing nif from the equation)
    - email for staff
        - Why: no VAT field in res_user
- Domain data: nif, vat, email...
    - vat: vat code with country prefix
        - TOCHECK: passports?
    - nif: vat but removing ES if starts with ES, used only to communicate with the user (internally a vat, use sandwich)
        - vat -> nif remove leading ES
        - nif -> vat, check if it validates as nif, if so, add ES
        - We reduce it into a presentation issue to present vats as nifs, so we delegate that to the API.

- Login is used just to login, erp turns it into a username.
- Username is used along to refer the user in api-erp communications
- NIFS are detected and turned into VATS
- VATS with ES are turned NIFS for presentation purposes (spanish users do not identify a VAT, but a NIF)

