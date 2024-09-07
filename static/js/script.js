document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const signupForm = document.getElementById('signupForm');
    
    if (loginForm) {
        const emailInput = document.getElementById('email');
        const passwordInput = document.getElementById('password');
        const emailError = document.getElementById('emailError');
        const passwordError = document.getElementById('passwordError');
    
        loginForm.addEventListener('submit', function(event) {
            let isValid = true;
    
            // Clear previous errors
            emailError.textContent = '';
            passwordError.textContent = '';

            // Clear Flask flashed messages via AJAX before form submission
            clearFlaskMessages();
    
            // Validate email
            const email = emailInput.value;
            if (!email) {
                emailError.textContent = 'Email address is required';
                isValid = false;
            } else if (!isValidEmail(email)) {
                emailError.textContent = 'Please enter a valid email address';
                isValid = false;
            } else {
                emailError.textContent = '';
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
            } else {
                passwordError.textContent = '';
            }
    
            // If any validation fails, prevent form submission
            if (!isValid) {
                event.preventDefault();
            }
            
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
            let isValid = true;
    
            // Clear previous errors
            emailError.textContent = '';
            passwordError.textContent = '';
            repasswordError.textContent = '';

            // Clear Flask flashed messages via AJAX before form submission
            clearFlaskMessages();
    
            // Validate email
            const email = emailInput.value;
            if (!email) {
                emailError.textContent = 'Email address is required';
                isValid = false;
            } else if (!isValidEmail(email)) {
                emailError.textContent = 'Please enter a valid email address';
                isValid = false;
            } else {
                emailError.textContent = '';
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
                passwordError.textContent = 'Requires letter,digit and special char';
                isValid = false;
            } else {
                passwordError.textContent = '';
            }
    
            // Validate re-entered password
            const repassword = repasswordInput.value;
            if (!repassword) {
                repasswordError.textContent = 'Please re-enter your password';
                isValid = false;
            } else if (password !== repassword) {
                repasswordError.textContent = 'Passwords do not match';
                isValid = false;
            } else {
                repasswordError.textContent = '';
            }
    
            // If any validation fails, prevent form submission
            if (!isValid) {
                event.preventDefault();
            }
        });
    }
    function clearFlaskMessages() {
        // Directly remove flashed messages from the DOM
        const flashedMessages = document.querySelectorAll('.flash-message');
        flashedMessages.forEach(message => message.remove());
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
