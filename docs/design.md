# Design choices

## Roles

We identified 3 roles

- Admin: Can provision users
    - ERP using the super secret key
- Staff: Can hijack users
    - TOVALIDATE: res.user?
- Customer: Plain users
    - Customer valid res_partner with the `customer` category.

## Provisining use cases

Definicions:
- provided data: the ones provided by the user on the wizard fields
    - VAT
    - Mail

Base case:

0. User provides data
1. Wizard verifies that user has not a partner address
2. Wizard creates the partner with provided data
3. Wizard creates the partner_address with provide data
4. Wizard links user to the partner_address
5. Wizard adds the category

Excepcions:

2.a. Wizard detects that there is one existing partner with the same vat
2.a.1. Wizard chooses the first address
2.a.2. Wizard warns operator about an existing partner and shows previous email
2.a.3. User choses which email to keep
2.a.4. Wizard updates the selected email
2.a.5. Go to step 4

2.b. Wizard detects that there is **more than one** existing partner with the same vat
2.b.1. Wizard shows a warning explaining the case and aborts

1.a. Wizard detects that the user is already relatated to an address
1.a.0. Wizard detects that the partner has not have the category
1.a.1. Wizard detects that the related vat matches
1.a.2. Wizard detects that the related address is 0 for the partner
1.a.3. Wizard chooses the first address
1.a.4. Wizard detects that the related email matches
1.a.5. Go to step 5

1.a.0.a. Wizard detects that the partner has the category
1.a.0.a.1. Shows messages and abort

1.a.1.a. Wizard detects that the related vat missmatches
1.a.1.a.1. Shows messages and abort

1.a.2.a. Wizard detects that the related address is not zero
1.a.2.a.1. Shows messages and abort

1.a.4.a. Wizard detects that the related email missmatches
1.a.4.a.1. Goto 2.a.2.



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

