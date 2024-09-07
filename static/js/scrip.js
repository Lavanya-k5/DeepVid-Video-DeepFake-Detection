document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const signupForm = document.getElementById('signupForm');
    
    function checkDBConnection(callback) {
        // Perform AJAX request to check database connection
        var xhr = new XMLHttpRequest();
        xhr.open('GET', '/check_db_connection', true);
        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE) {
                if (xhr.status === 200) {
                    var response = JSON.parse(xhr.responseText);

                    // Check if database connection is successful
                    if (response.success) {
                        callback(true); // Connection successful
                    } else {
                        alert(response.error); // Display error message
                        callback(false); // Connection failed
                    }
                } else {
                    // Error handling for AJAX request
                    alert('Error occurred while checking database connection.');
                    callback(false); // Connection failed
                }
            }
        };
        xhr.send(); // Send the AJAX request
    }
    function handleFormSubmit(event, form, validateForm) {
        event.preventDefault(); // Prevent the form from submitting immediately

        checkDBConnection(function(success) {
            if (success) {
                // If DB connection is successful, validate the form
                if (validateForm()) {
                    console.log('Form validation successful');
                    form.submit(); // Submit the form if validation passes
                }
            }
        });
    }
    if (loginForm) {
        const emailInput = document.getElementById('email');
        const passwordInput = document.getElementById('password');
        const emailError = document.getElementById('emailError');
        const passwordError = document.getElementById('passwordError');

        loginForm.addEventListener('submit', function(event) {
            handleFormSubmit(event, loginForm, function() {
                let isValid = true;

                // Clear previous errors
                emailError.textContent = '';
                passwordError.textContent = '';

                // Validate email
                const email = emailInput.value;
                if (!email) {
                    emailError.textContent = 'Email address is required';
                    isValid = false;
                } else if (!isValidEmail(email)) {
                    emailError.textContent = 'Please enter a valid email address';
                    isValid = false;
                }

                // Validate password
                const password = passwordInput.value;
                if (!password) {
                    passwordError.textContent = 'Password is required';
                    isValid = false;
                }

                return isValid;
            });
        });
    }

    if (signupForm) {
        const emailInput = document.getElementById('email');
        const passwordInput = document.getElementById('password');
        const repasswordInput = document.getElementById('repassword');
        const emailError = document.getElementById('emailError');
        const passwordError = document.getElementById('passwordError');
        const repasswordError = document.getElementById('repasswordError');

        signupForm.addEventListener('submit', function(event) {
            handleFormSubmit(event, signupForm, function() {
                let isValid = true;

                // Clear previous errors
                emailError.textContent = '';
                passwordError.textContent = '';
                repasswordError.textContent = '';

                // Validate email
                const email = emailInput.value;
                if (!email) {
                    emailError.textContent = 'Email address is required';
                    isValid = false;
                } else if (!isValidEmail(email)) {
                    emailError.textContent = 'Please enter a valid email address';
                    isValid = false;
                }

                // Validate password
                const password = passwordInput.value;
                if (!password) {
                    passwordError.textContent = 'Password is required';
                    isValid = false;
                } else if (password.length < 8 || password.length > 15) {
                    passwordError.textContent = 'Password must be 8-15 characters long';
                    isValid = false;
                } else if (!isValidPassword(password)) {
                    passwordError.textContent = 'Requires letter, digit, and special char';
                    isValid = false;
                }

                // Validate re-entered password
                const repassword = repasswordInput.value;
                if (!repassword) {
                    repasswordError.textContent = 'Please re-enter your password';
                    isValid = false;
                } else if (password !== repassword) {
                    repasswordError.textContent = 'Passwords do not match';
                    isValid = false;
                }

                return isValid;
            });
        });
    }
    
    function isValidEmail(email) {
        // Simple email validation regex ensuring it ends with @gmail.com
        const emailRegex = /^[^\s@]+@gmail\.com$/;
        return emailRegex.test(email);
    }

    function isValidPassword(password) {
        //Password validation rules
        const passwordRegex = /^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*?&^#])[A-Za-z\d@$!%*?&^#]{8,15}$/;
        return passwordRegex.test(password);
    }
    
   // Condition 2: Check for at least one letter, one digit, and one special character
   //const hasLetter = /[A-Za-z]/.test(password);
   //const hasDigit = /\d/.test(password);
   //const hasSpecialChar = /[@$!%*?&^#]/.test(password);
   //if (!hasLetter || !hasDigit || !hasSpecialChar) {
     //  return false;}
   
    // Sticky header functionality
    window.onscroll = function() {myFunction()};

    // Get the header
    var header = document.getElementById("Myheader");

    // Get the offset position of the navbar
    var sticky = header.offsetTop;

    // Add the sticky class to the header when you reach its scroll position. Remove "sticky" when you leave the scroll position
    function myFunction() {
        if (window.pageYOffset > sticky) {
            header.classList.add("sticky");
        } else {
            header.classList.remove("sticky");
        }
    }
});
