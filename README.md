# Technical Lesson: Flask-SQLAlchemy Validations

In our earlier example, we looked at validating an email address.
In this lesson we'll use that same example and extend our validations a bit.

Here's where our code left off in the example:

```py
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
db = SQLAlchemy()

class EmailAddress(db.Model):
    __tablename__ = 'emailaddress'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String)
    backup_email = db.Column(db.String)

    @validates('email', 'backup_email')
    def validate_email(self, key, address):
        if '@' not in address:
            raise ValueError("Email must have an '@' in the address.")
        return address
```

## Scenario

Our current validation is not enough for what the system needs to check for emails.

We need to extend our validations to check for the following:
* Email is present and a string.
* Emails should not be duplicates or already exist in our system.
* Our database requires that emails not be longer than 254 characters.
* Our company has decided to not accept hotmail or yahoo emails
  * > Note: this constraint is just for the purpose of example. Typically, we would not want to limit our users' email providers.

## Tools & Resources

- [GitHub Repo](https://github.com/learn-co-curriculum/flask-sqlalchemy-validations-technical-lesson)
- [Changing Attribute Behavior - SQLAlchemy](https://docs.sqlalchemy.org/en/14/orm/mapped_attributes.html)

## Set Up

Run `pipenv install` to create your virtual environment and `pipenv shell` to
enter the virtual environment.

```console
pipenv install && pipenv shell
```

This project has starter code for a `EmailAddress` model and a starter seed file. To
get create the database run:

```console
$ cd server
$ flask db init
$ flask db migrate -m 'init migration'
$ flask db upgrade head
$ python seed.py
```

Feel free to add to the seed file as you go to test validations or 
use `flask shell`. We'll also test all validations in the shell at the end 
of the lesson.

## Instructions
### Task 1: Define the Problem

Our application currently permits invalid, inconsistent, or duplicate email data. The existing 
validation only checks for the presence of an "@" symbol, which is insufficient in a real-world system.

This opens us up to several risks:
* Users can submit blank or malformed email addresses.
* Duplicate emails can be stored, compromising identity or login mechanisms.
* Emails might exceed the maximum length allowed by email standards or database column constraints.
* Certain domains (like hotmail.com or yahoo.com) are disallowed due to company policy but are not being 
filtered.

Without stronger validations, the database becomes unreliable, and any downstream processes (like sending 
email, filtering users, etc.) may break.

### Task 2: Determine the Design

We'll improve validation by embedding checks directly into the SQLAlchemy model using the @validates() decorator. Here's how:

1. Use a centralized validation method:
  * Validate both email and backup_email with a single method, using the key argument to distinguish between them if needed.

2. Enforce multiple validation rules:
  * Presence: Ensure the email is not blank or null.
  * Type check: Confirm the email is a string.
  * Format: Ensure it includes an "@" character.
  * Length: Cap length at 254 characters (the internet standard max).
  * Uniqueness: Query the database for duplicates (note: real production apps should use unique constraints at the DB level too).
  * Restricted domains: Check domain part of the email and block disallowed providers.

3. Raise clear, specific ValueErrors for each invalid case so that errors are easy to interpret.

4. Use SQLAlchemy's session context (db.session.query()) to check existing records for uniqueness.

This layered validation process allows the model to guard against invalid data before anything is committed to the database.

### Task 3: Develop, Test, and Refine the Code

#### Step 1: Add Validation for Presence

Let's start by creating our validation to test presence. All we need to check here
is that email is a truthy value, instead of an empty string or `None`.

```python
    @validates('email', 'backup_email')
    def validate_email(self, key, address):
        # check for presence
        if not address:
            raise ValueError("Email must be present.")
        
        if '@' not in address:
            raise ValueError("Email must have an '@' in the address.")

        return address
```

#### Step 2: Add Validation for Type

Next, let's build our validation for type. HEre we are testing that the 
email is in fact a string. We'll use the `isinstance()` Python function.

```python
    @validates('email', 'backup_email')
    def validate_email(self, key, address):
        # check for presence
        if not address:
            raise ValueError("Email must be present.")

        # Check for type
        if not isinstance(address, str):
            raise ValueError("Email must be a string.")
        
        if '@' not in address:
            raise ValueError("Email must have an '@' in the address")

        return address
```

#### Step 3: Add Validation for Uniqueness

To check for duplicates, We need query the database and verify the email 
doesn't already exist. We can do so by filtering our SQL query by the email
we are validating and then verifying that the email returned by the database is None.

```python
# check for duplicate
duplicate_email = db.session.query(EmailAddress.id).filter_by(email = address).first()
if duplicate_email is not None:
    raise ValueError("Email must be unique.")
```

#### Step 4: Add Validation for Length

Now, we need to test the length of the email. For this, we can use Python's `len()`.

```python
# check email not too long
if len(address) > 254:
    raise ValueError("Email is too long.")
```

#### Step 5: Add Validation for Domain

Finally, we need to test the domain of the email. Python's `in` will come in handy here.

```python
# reject hotmail and yahoo emails
if address.split("@")[1] in ["hotmail.com", "yahoo.com"]:
    raise ValueError("Email cannot be a hotmail or yahoo address.")
```

#### Step 6: Verify your Code

To test our code, let's pop into `flask shell`.

```bash
flask shell
```

Test presence:
```bash
EmailAddress(email='', backup_email = 'test@gmail.com')
# => ... ValueError: Email must be present.
```

Test type:
```bash
EmailAddress(email=982, backup_email = 'test@gmail.com')
# => ... ValueError: Email must be a string.
```

Test uniqueness (ensure seed.py has been run, back_up email here then should already have been used):
```bash
EmailAddress(email='test@gmail.com', backup_email = 'email@email.com')
# => ... ValueError: Email must be unique.
```

Test for long emails:
```bash
EmailAddress(email='hgdbdkjwkqwjaekjnafwjknfwkjnwjkfjknjkqjwnfnrkjqnkjfbnqwjkrfbnjwqbnjfnqwjklnfjkwqnfkjnqwkjfnkqwenfkwqnkfjnqewkjnekw  fqnfkjqnwjknfkj wenfjknqwkjfnjkqwnfjknqewkjfnkj wnekefnkjew nekjnqkjenfkjnqwkjfnqwhfjiuqhwfkjvbvkjnqwkcndkawbncjkbdjkwbcjkawckjndawjkcnfkjawenckwnfkqnfkjn@gmail.com', backup_email = 'test@gmail.com')
# => ... ValueError: Email is too long.
```

Test for domain exclusion:
```bash
EmailAddress(email='test@hotmail.com', backup_email = 'test@gmail.com')
# => ... ValueError: Email cannot be a hotmail or yahoo address.

EmailAddress(email='test@yahoo.com', backup_email = 'test@gmail.com')
# => ... ValueError: Email cannot be a hotmail or yahoo address.
```

> Note: It's best practice to write a test suite for these edge cases and also 
to verify that valid emails pass the validations.

#### Step 7: Commit and Push Git History

* Commit and push your code:

```bash
git add .
git commit -m "final solution"
git push
```

* If you created a separate feature branch, remember to open a PR on main and merge.

### Task 4: Document and Maintain

Best Practice documentation steps:
* Add comments to the code to explain purpose and logic, clarifying intent and functionality of your code to other developers.
* Update README text to reflect the functionality of the application following https://makeareadme.com. 
  * Add screenshot of completed work included in Markdown in README.
* Delete any stale branches on GitHub
* Remove unnecessary/commented out code
* If needed, update git ignore to remove sensitive data

## Considerations
### Order of validations matters
Check for presence and type before using string methods (like .split()), or you’ll 
raise the wrong kind of error.

### Avoid double queries
Uniqueness checks should apply only where necessary to minimize DB load.

### Raise informative errors
This is important in test-driven labs, where learners and graders rely on specific 
messaging, but also for real applications.

### Backup email handling
If backup_email is allowed to be null or duplicate, clarify this in the logic (e.g., 
skip uniqueness check for backup fields).

### Database vs Model-Level Constraints
These are not the same. Model validations ensure clean data before a commit; database 
constraints are a final safeguard. It's important to validate at as many levels as 
possible: database, model, schema, and even frontend UI validations in HTML forms.