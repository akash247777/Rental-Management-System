// Dashboard page JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Check authentication
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = 'index.html';
        return;
    }

    // Set up sidebar menu functionality
    setupSidebarMenu();

    // Function to handle unauthorized responses
    async function handleUnauthorized() {
        alert('Your session has expired. Please log in again.');
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = 'index.html';
    }

    // Function to make authenticated API calls
    async function makeAuthenticatedRequest(url, options = {}) {
        try {
            // Check if token exists
            const token = localStorage.getItem('token');
            if (!token) {
                console.error('No authentication token found');
                window.location.href = 'index.html';
                return { error: true, message: 'Authentication required. Please login.' };
            }

            // Add base URL if it's a relative path
            const apiUrl = url.startsWith('http') ? url : `http://localhost:5000${url}`;
            console.log(`Making request to ${apiUrl}`);

            // Set default headers with auth token
            const defaultOptions = {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            };

            // Merge options
            const requestOptions = { ...defaultOptions, ...options };

            console.log(`Making request to ${apiUrl}`);
            const response = await fetch(apiUrl, requestOptions);

            // Handle unauthorized requests (expired token)
            if (response.status === 401) {
                console.error('Authentication failed: Token expired or invalid');
                localStorage.removeItem('token');
                window.location.href = 'index.html';
                return { error: true, message: 'Your session has expired. Please login again.' };
            }

            // Parse JSON response
            const data = await response.json();

            // Handle 404 Not Found responses
            if (response.status === 404) {
                console.error('Resource not found:', data.message || 'Item not found');
                return { error: true, status: 404, message: data.message || 'Item not found' };
            }

            // Check for other API errors
            if (!response.ok) {
                console.error('API error:', data.message || 'Unknown error');
                return { error: true, status: response.status, message: data.message || `Request failed with status: ${response.status}` };
            }

            return data;
        } catch (error) {
            console.error('Request error:', error);
            return { error: true, message: error.message || 'Network error occurred' };
        }
    }

    // Toggle sidebar
    const toggleBtn = document.querySelector('.toggle-btn');
    const sidebar = document.querySelector('.sidebar');

    if(toggleBtn && sidebar) {
        toggleBtn.addEventListener('click', function() {
            sidebar.classList.toggle('active');
        });
    }

    // Search form
    const searchForm = document.getElementById('searchForm');

    if(searchForm) {
        searchForm.addEventListener('submit', async function(e) {
            e.preventDefault();

            const siteSearch = document.getElementById('siteSearch').value;

            if(!siteSearch) {
                alert('Please enter a site ID');
                return;
            }

            try {
                // First try to search directly by site ID
                const searchValue = siteSearch.trim();
                console.log("Searching for site ID:", searchValue);
                const data = await makeAuthenticatedRequest(`/api/search?term=${encodeURIComponent(searchValue)}&site_id_search=true`);
                if (!data) return;

                console.log("Search API response:", data);

                if(data.results && data.results.length > 0) {
                    // If search found a site, load it directly
                    const site = data.results[0];
                    console.log("Found site:", site);

                    // Make sure we have a valid site_id
                    if (!site.site_id) {
                        console.error("Missing site_id in search result");
                        alert('Invalid search result: missing site ID');
                        return;
                    }

                    const siteData = await makeAuthenticatedRequest(`/api/sites?site_id=${site.site_id}`);

                    if (siteData) {
                        console.log("Site details loaded:", siteData);
                        updateSiteData(siteData);
                    } else {
                        console.error("Failed to load site details");
                        alert('Failed to load site details');
                    }
                } else {
                    console.error("Site not found:", data);
                    alert(data.message || 'Site not found');
                }
            } catch(error) {
                console.error('Search error:', error);
                alert('An error occurred while searching');
            }
        });
    }

    // New Entry Link
    const newEntryLink = document.getElementById('newEntryLink');

    if(newEntryLink) {
        newEntryLink.addEventListener('click', function(e) {
            e.preventDefault();
            window.location.href = 'new-entry.html';
        });
    }

    // Report Link
    const reportLink = document.getElementById('reportLink');

    if(reportLink) {
        reportLink.addEventListener('click', function(e) {
            e.preventDefault();
            window.location.href = 'reports.html';
        });
    }

    // Edit Button
    const editBtn = document.getElementById('editBtn');
    let currentSiteId = null; // Store current site ID

    if(editBtn) {
        // Create cancel button but keep it hidden initially
        const cancelBtn = document.createElement('button');
        cancelBtn.textContent = 'Cancel';
        cancelBtn.className = 'btn btn-cancel';
        cancelBtn.style.display = 'none';
        cancelBtn.id = 'cancelBtn';
        editBtn.parentNode.insertBefore(cancelBtn, editBtn.nextSibling);

        editBtn.addEventListener('click', async function() {
            if (!editBtn.classList.contains('editing')) {
                // Show authentication modal first
                const authModal = document.getElementById('authModal');
                authModal.style.display = 'flex';

                // Remove any existing event listeners to prevent duplicates
                const authForm = document.getElementById('authForm');
                const newAuthForm = authForm.cloneNode(true);
                authForm.parentNode.replaceChild(newAuthForm, authForm);

                // Handle authentication form submission
                newAuthForm.addEventListener('submit', function(e) {
                    e.preventDefault();
                    const username = document.getElementById('authUsername').value;
                    const password = document.getElementById('authPassword').value;

                    if (username === 'admin' && password === 'admin@123') {
                        authModal.style.display = 'none';
                        newAuthForm.reset();
                        startEditing(); // Call the existing edit functionality
                    } else {
                        const errorMsg = document.querySelector('#authModal .error-message') ||
                            (() => {
                                const div = document.createElement('div');
                                div.className = 'error-message';
                                div.style.color = 'red';
                                div.style.marginTop = '10px';
                                newAuthForm.appendChild(div);
                                return div;
                            })();
                        errorMsg.textContent = 'Invalid credentials';
                        errorMsg.style.display = 'block';
                    }
                });

                // Handle cancel button
                const cancelAuth = document.getElementById('cancelAuth');
                cancelAuth.addEventListener('click', function() {
                    authModal.style.display = 'none';
                    newAuthForm.reset();
                    const errorMsg = document.querySelector('#authModal .error-message');
                    if (errorMsg) errorMsg.style.display = 'none';
                });

                // Handle modal close button if it exists
                const closeBtn = authModal.querySelector('.close');
                if (closeBtn) {
                    closeBtn.addEventListener('click', function() {
                        authModal.style.display = 'none';
                        newAuthForm.reset();
                        const errorMsg = document.querySelector('#authModal .error-message');
                        if (errorMsg) errorMsg.style.display = 'none';
                    });
                }
            } else {
                try {
                    const updatedData = {};
                    const valueElements = document.querySelectorAll('[id$="_value"]');

                    // Define date fields with exact column names
                    const dateFields = {
                        'agreement_date_value': 'AGREEMENT DATE',
                        'rent_position_date_value': 'RENT POSITION DATE',
                        'rent_effective_date_value': 'RENT EFFECTIVE DATE',
                        'agreement_valid_upto_value': 'AGREEMENT VALID UPTO',
                        'current_date_value': 'CURRENT DATE',
                        'current_date1_value': 'CURRENT DATE 1',
                        'validity_date_value': 'VALIDITY DATE',
                        'doo_value': 'D.O.O'
                    };

                    valueElements.forEach(element => {
                        // Remove editable attributes
                        element.contentEditable = 'false';
                        element.classList.remove('editable');

                        let value = element.textContent.trim();

                        // Skip empty or N/A values
                        if (!value || value === 'N/A') {
                            return;
                        }

                        // Check if this is a date field
                        if (dateFields[element.id]) {
                            const parts = value.split('-');
                            if (parts.length === 3) {
                                // Convert from DD-MM-YYYY to YYYY-MM-DD
                                value = `${parts[2]}-${parts[1].padStart(2, '0')}-${parts[0].padStart(2, '0')}`;
                                updatedData[dateFields[element.id]] = value; // Use the mapped column name
                            }
                        } else {
                            // Handle percentage fields
                            const fieldName = element.id.replace('_value', '');
                            if (fieldName.includes('percentage') || fieldName === 'hike') {
                                value = parseFloat(value.replace('%', ''));
                            }

                            updatedData[fieldName] = value;
                        }
                    });

                    console.log('Data being sent to server:', updatedData);
                    await updateSite(currentSiteId, updatedData);

                    // Reset the edit mode
                    editBtn.textContent = 'Edit';
                    editBtn.classList.remove('editing');
                    cancelBtn.style.display = 'none';

                } catch (error) {
                    console.error('Error updating site:', error);
                    alert('Error updating site: ' + error.message);
                }
            }
        });

        // Cancel button handler
        cancelBtn.addEventListener('click', async function() {
            try {
                // Remove editable state from all elements
                const valueElements = document.querySelectorAll('[id$="_value"]');
                valueElements.forEach(element => {
                    // Remove editable attributes
                    element.contentEditable = 'false';
                    element.classList.remove('editable');

                    // Remove any helper text
                    const helpText = element.querySelector('.form-text');
                    if (helpText) {
                        helpText.remove();
                    }

                    // For percentage fields, add back the % symbol if needed
                    if (element.id.includes('percentage')) {
                        let value = element.textContent.trim();
                        if (value && value !== 'N/A' && !value.includes('%')) {
                            element.textContent = value + '%';
                        }
                    }
                });

                // Reset the form to its original state
                editBtn.textContent = 'Edit';
                editBtn.classList.remove('editing');
                cancelBtn.style.display = 'none';

                // Refresh the display with original data
                if (currentSiteId) {
                    const response = await makeAuthenticatedRequest(`/api/sites?site_id=${currentSiteId}`);
                    if (!response.error) {
                        updateSiteData(response);
                    }
                }
            } catch (error) {
                console.error('Error canceling edit:', error);
            }
        });
    }

    // Function to update site data on the server
    async function updateSite(siteId, data) {
        try {
            if (!siteId) {
                console.error('Cannot update site: Missing site ID');
                alert('Error: Missing site ID');
                return;
            }

            // Double check site_id is included in the data
            data.site_id = siteId;

            console.log('Updating site with ID:', siteId);
            console.log('Update data:', data);

            const result = await makeAuthenticatedRequest(`/api/sites/${siteId}`, {
                method: 'PUT',
                body: JSON.stringify(data)
            });

            if (result.error) {
                console.error('Update error:', result.message);
                alert(result.message || 'Error updating site');
                return;
            }

            console.log('Site updated successfully');
            alert('Site updated successfully');

            // Refresh the display with updated data
            const siteData = await makeAuthenticatedRequest(`/api/sites?site_id=${siteId}`);

            if (siteData.error) {
                console.error('Error fetching updated site data:', siteData.message);
                return;
            }

            console.log('Refreshing display with updated data');
            updateSiteData(siteData);
        } catch (error) {
            console.error('Update error:', error);
            alert('An error occurred while updating the site: ' + error.message);
        }
    }

    // Logout
    const logoutLink = document.querySelector('a[href="index.html"]');
    if(logoutLink) {
        logoutLink.addEventListener('click', function(e) {
            e.preventDefault();
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            window.location.href = 'index.html';
        });
    }

    // Update site data in the UI
    function updateSiteData(siteData) {
        console.log("Raw site data received in updateSiteData:", siteData);

        if (!siteData) {
            console.error("No site data provided");
            return;
        }

        // Handle different response formats
        let processedData;

        if (Array.isArray(siteData)) {
            // If it's an array, use the first item
            console.log("Response is an array, using first item");
            processedData = { ...siteData[0] };
        } else if (typeof siteData === 'object') {
            // If it's an object, clone it
            processedData = { ...siteData };

            // If it has a site property that's an object, use that
            if (siteData.site && typeof siteData.site === 'object') {
                console.log("Found nested site object, using that");
                processedData = { ...siteData.site };
            }
        } else {
            console.error("Unexpected data format:", typeof siteData);
            return;
        }

        // Convert div property to expected format if needed
        if (processedData.division && !processedData.div) {
            processedData.div = processedData.division;
        }

        console.log("Processed data:", processedData);

        // Helper function to safely update element text content
        function updateElement(id, value) {
            const element = document.getElementById(id);
            if (element) {
                console.log(`Updating element #${id} with value:`, value);
                // Only use 'N/A' if value is actually null, undefined, or empty string
                element.textContent = (value !== null && value !== undefined && value !== '') ? value : 'N/A';
            } else {
                console.warn(`Element with ID ${id} not found`);
            }
        }

        // Helper function to get value from data with multiple potential field names
        function getFieldValue(data, fieldNames) {
            for (const fieldName of fieldNames) {
                if (data[fieldName] !== undefined && data[fieldName] !== null && data[fieldName] !== '') {
                    return data[fieldName];
                }
            }
            return null;
        }

        // Check for specific fields with console logging
        console.log("Site ID:", getFieldValue(processedData, ['SITE', 'site', 'site_id']));
        console.log("Store Name:", getFieldValue(processedData, ['STORE NAME', 'store_name']));
        console.log("Region:", getFieldValue(processedData, ['REGION', 'region']));
        console.log("Div:", getFieldValue(processedData, ['DIV', 'div']));
        console.log("Present Rent:", getFieldValue(processedData, ['PRESENT RENT', 'present_rent']));
        console.log("HIKE %:", getFieldValue(processedData, ['HIKE %', 'hike_percentage']));
        console.log("ASST MANAGER:", getFieldValue(processedData, ['ASST MANAGER', 'asst_manager']));

        // Update site ID with both possible IDs to ensure it's displayed
        updateElement('site_value', getFieldValue(processedData, ['SITE', 'site', 'site_id']));

        // Update basic info elements
        updateElement('store_name_value', getFieldValue(processedData, ['STORE NAME', 'store_name']));
        updateElement('region_value', getFieldValue(processedData, ['REGION', 'region']));
        updateElement('div_value', getFieldValue(processedData, ['DIV', 'div']));
        updateElement('manager_value', getFieldValue(processedData, ['MANAGER', 'manager']));
        updateElement('asst_manager_value', getFieldValue(processedData, ['ASST MANAGER', 'asst_manager']));
        updateElement('executive_value', getFieldValue(processedData, ['EXECUTIVE', 'executive']));
        updateElement('doo_value', getFieldValue(processedData, ['D.O.O', 'doo']));
        updateElement('sqft_value', getFieldValue(processedData, ['SQ.FT', 'sqft']));
        updateElement('agreement_date_value', getFieldValue(processedData, ['AGREEMENT DATE', 'agreement_date']));
        updateElement('rent_position_date_value', getFieldValue(processedData, ['RENT POSITION DATE', 'rent_position_date']));
        updateElement('rent_effective_date_value', getFieldValue(processedData, ['RENT EFFECTIVE DATE', 'rent_effective_date']));
        updateElement('agreement_valid_upto_value', getFieldValue(processedData, ['AGREEMENT VALID UPTO', 'agreement_valid_upto']));
        updateElement('current_date_value', getFieldValue(processedData, ['CURRENT DATE', 'current_date']));
        updateElement('lease_period_value', getFieldValue(processedData, ['LEASE PERIOD', 'lease_period']));
        updateElement('rent_free_period_days_value', getFieldValue(processedData, ['RENT FREE PERIOD DAYS', 'rent_free_period_days']));
        updateElement('rent_effective_amount_value', getFieldValue(processedData, ['RENT EFFECTIVE AMOUNT', 'rent_effective_amount']));
        updateElement('present_rent_value', getFieldValue(processedData, ['PRESENT RENT', 'present_rent']));

        // Special handling for hike percentage to ensure it's displayed with the % symbol
        const hikeValue = getFieldValue(processedData, ['HIKE %', 'hike_percentage']);
        if (hikeValue !== null && hikeValue !== undefined) {
            let formattedHikeValue = hikeValue;
            try {
                // Parse as float if it's a string
                if (typeof formattedHikeValue === 'string') {
                    formattedHikeValue = parseFloat(formattedHikeValue);
                }

                // Format the value with the % symbol if it's a number
                if (!isNaN(formattedHikeValue)) {
                    formattedHikeValue = formattedHikeValue + '%';
                }
            } catch (e) {
                console.error("Error formatting hike percentage:", e);
            }
            updateElement('hike_percentage_value', formattedHikeValue);
        } else {
            updateElement('hike_percentage_value', 'N/A');
        }

        // Update remaining elements
        updateElement('hike_year_value', getFieldValue(processedData, ['HIKE YEAR', 'hike_year']));
        updateElement('rent_deposit_value', getFieldValue(processedData, ['RENT DEPOSIT', 'rent_deposit']));
        updateElement('owner_name1_value', getFieldValue(processedData, ['OWNER NAME-1', 'owner_name1']));
        updateElement('owner_name2_value', getFieldValue(processedData, ['OWNER NAME-2', 'owner_name2']));
        updateElement('owner_name3_value', getFieldValue(processedData, ['OWNER NAME-3', 'owner_name3']));
        updateElement('owner_name4_value', getFieldValue(processedData, ['OWNER NAME-4', 'owner_name4']));
        updateElement('owner_name5_value', getFieldValue(processedData, ['OWNER NAME-5', 'owner_name5']));
        updateElement('owner_name6_value', getFieldValue(processedData, ['OWNER NAME-6', 'owner_name6']));
        updateElement('owner_mobile_value', getFieldValue(processedData, ['OWNER MOBILE', 'owner_mobile']));
        updateElement('current_date1_value', getFieldValue(processedData, ['CURRENT DATE 1', 'current_date1']));
        updateElement('validity_date_value', getFieldValue(processedData, ['VALIDITY DATE', 'validity_date']));
        updateElement('gst_number_value', getFieldValue(processedData, ['GST NUMBER', 'gst_number']));
        updateElement('pan_number_value', getFieldValue(processedData, ['PAN NUMBER', 'pan_number']));

        // Special handling for TDS percentage to ensure it's displayed with the % symbol
        const tdsValue = getFieldValue(processedData, ['TDS PERCENTAGE', 'tds_percentage']);
        if (tdsValue !== null && tdsValue !== undefined) {
            let formattedTdsValue = tdsValue;
            try {
                // Parse as float if it's a string
                if (typeof formattedTdsValue === 'string') {
                    formattedTdsValue = parseFloat(formattedTdsValue);
                }
                // Format the value with the % symbol if it's a number
                if (!isNaN(formattedTdsValue)) {
                    formattedTdsValue = formattedTdsValue + '%';
                }
            } catch (e) {
                console.error("Error formatting TDS percentage:", e);
            }
            updateElement('tds_percentage_value', formattedTdsValue);
        } else {
            updateElement('tds_percentage_value', 'N/A');
        }

        updateElement('mature_value', getFieldValue(processedData, ['MATURE', 'mature']));
        updateElement('status_value', getFieldValue(processedData, ['STATUS', 'status']));
        updateElement('remarks_value', getFieldValue(processedData, ['REMARKS', 'remarks']));

        // Make sure the site details section is visible
        const siteDetailsSection = document.getElementById('site_details_section');
        if (siteDetailsSection) {
            siteDetailsSection.style.display = 'block';
        }
    }

    // Helper function to format currency values
    function formatCurrency(amount) {
        // Format number as currency
        return new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: 'INR',
            maximumFractionDigits: 0
        }).format(amount);
    }

    // Helper function to format dates
    function formatDate(dateString) {
        if (!dateString) return '';
        const date = new Date(dateString);
        if (isNaN(date.getTime())) return dateString; // Return original string if invalid date
        return date.toLocaleDateString('en-IN');
    }

    // Add this helper function at the top level
    function formatDateForDisplay(dateStr) {
        if (!dateStr || dateStr === 'N/A') return '';

        try {
            // Trim and check for empty string
            dateStr = dateStr.trim();
            if (!dateStr) return '';

            // Handle different date formats
            if (dateStr.includes('-')) {
                const parts = dateStr.split('-');

                // Handle YYYY-MM-DD format (convert to DD-MM-YYYY)
                if (parts.length === 3 && parts[0].length === 4) {
                    console.log(`Converting YYYY-MM-DD format ${dateStr} to DD-MM-YYYY`);
                    // Ensure day and month are zero-padded
                    const day = parts[2].padStart(2, '0');
                    const month = parts[1].padStart(2, '0');
                    const year = parts[0];
                    return `${day}-${month}-${year}`;
                }
                // Handle DD-MM-YYYY format (keep as is but ensure proper formatting)
                else if (parts.length === 3 && parts[2].length === 4) {
                    console.log(`Ensuring proper DD-MM-YYYY format for ${dateStr}`);
                    // Ensure day and month are zero-padded
                    const day = parts[0].padStart(2, '0');
                    const month = parts[1].padStart(2, '0');
                    const year = parts[2];
                    return `${day}-${month}-${year}`;
                }
                // Any other format with dashes, return as is
                return dateStr;
            }

            // Handle slash formats (convert to dashes)
            if (dateStr.includes('/')) {
                const parts = dateStr.split('/');

                // Handle YYYY/MM/DD format
                if (parts.length === 3 && parts[0].length === 4) {
                    console.log(`Converting YYYY/MM/DD format ${dateStr} to DD-MM-YYYY`);
                    return `${parts[2].padStart(2, '0')}-${parts[1].padStart(2, '0')}-${parts[0]}`;
                }
                // Handle DD/MM/YYYY format
                else if (parts.length === 3 && parts[2].length === 4) {
                    console.log(`Converting DD/MM/YYYY format ${dateStr} to DD-MM-YYYY`);
                    return `${parts[0].padStart(2, '0')}-${parts[1].padStart(2, '0')}-${parts[2]}`;
                }
                // Any other format with slashes, try to guess
                return dateStr.replace(/\//g, '-');
            }

            // Try to parse as a date object if all else fails
            try {
                const date = new Date(dateStr);
                if (!isNaN(date.getTime())) {
                    console.log(`Parsed ${dateStr} as Date object`);
                    const day = date.getDate().toString().padStart(2, '0');
                    const month = (date.getMonth() + 1).toString().padStart(2, '0');
                    const year = date.getFullYear();
                    return `${day}-${month}-${year}`;
                }
            } catch (parseError) {
                console.error('Date parsing error:', parseError);
            }

            // If everything fails, return original string
            return dateStr;
        } catch (e) {
            console.error('Date formatting error:', e);
            return dateStr;
        }
    }

    // Add this function to handle the edit mode start
    function startEditing() {
        // Starting edit mode
        let siteElement = document.getElementById('site_value');
        if (!siteElement) {
            siteElement = document.getElementById('site_id_value');
        }

        // Get the site ID value
        currentSiteId = siteElement ? siteElement.textContent.trim() : null;
        console.log("Current site ID for editing:", currentSiteId);

        if(!currentSiteId || currentSiteId === 'N/A') {
            alert('Error: No site ID found. Cannot edit.');
            return;
        }

        // Change button text to "Save" and show cancel button
        editBtn.textContent = 'Save';
        editBtn.classList.add('editing');
        cancelBtn.style.display = 'inline-block';

        // Make all value fields editable except site_id
        const valueElements = document.querySelectorAll('[id$="_value"]');
        valueElements.forEach(element => {
            // Skip the site_id field as it shouldn't be editable
            if (element.id === 'site_value') {
                return;
            }

            // Remove any existing event listeners and classes
            element.replaceWith(element.cloneNode(true));
            const newElement = document.getElementById(element.id);

            // Make the element content editable
            newElement.contentEditable = 'true';
            newElement.classList.add('editable');

            // For percentage fields, remove % for editing
            if (element.id.includes('percentage')) {
                let value = newElement.textContent;
                if (value && value !== 'N/A' && value.includes('%')) {
                    newElement.textContent = value.replace('%', '');
                }
            }

            // Add click event to highlight the field
            newElement.addEventListener('click', function() {
                this.focus();
            });
        });
    }

    async function searchSite() {
        try {
            const siteSearch = document.getElementById('siteSearch').value;
            if (!siteSearch.trim()) {
                alert('Please enter a site ID to search');
                return;
            }

            // Clear previous site details
            document.getElementById('siteDetails').innerHTML = '';
            document.getElementById('searchResults').innerHTML = '<p>Searching...</p>';

            // Clean and encode the search value
            const searchValue = siteSearch.trim().toUpperCase();
            console.log("Searching for site ID:", searchValue);

            // First try exact search
            const data = await makeAuthenticatedRequest(`/api/search?term=${encodeURIComponent(searchValue)}&site_id_search=true`);

            // Check if the request was successful
            if (data.error) {
                if (data.status === 404) {
                    // If not found and the search is just a number, try with SITE prefix
                    if (/^\d+$/.test(searchValue)) {
                        const sitePrefix = `SITE${searchValue.padStart(3, '0')}`;
                        console.log("No results found. Trying with prefix:", sitePrefix);
                        document.getElementById('searchResults').innerHTML = `<p>Trying with prefix: ${sitePrefix}...</p>`;

                        const prefixData = await makeAuthenticatedRequest(`/api/search?term=${encodeURIComponent(sitePrefix)}&site_id_search=true`);

                        if (prefixData.error) {
                            // Still no results
                            document.getElementById('searchResults').innerHTML = `
                                <p>No sites found for "${searchValue}" or "${sitePrefix}".</p>
                                <p>Site IDs are typically in the format "SITE001".</p>
                                <p>Try searching with the complete site ID.</p>
                            `;
                            return;
                        }

                        if (prefixData.results && prefixData.results.length > 0) {
                            displaySearchResults(prefixData.results[0]);
                            return;
                        } else {
                            document.getElementById('searchResults').innerHTML = `
                                <p>No sites found for "${searchValue}" or "${sitePrefix}".</p>
                                <p>Site IDs are typically in the format "SITE001".</p>
                                <p>Try searching with the complete site ID.</p>
                            `;
                            return;
                        }
                    } else {
                        document.getElementById('searchResults').innerHTML = `<p>${data.message || 'No sites found matching your search.'}</p>`;
                        return;
                    }
                } else {
                    // Handle other error statuses
                    document.getElementById('searchResults').innerHTML = `<p>Error: ${data.message || 'An error occurred during search'}</p>`;
                    return;
                }
            }

            // Process successful response
            if (data.results && data.results.length > 0) {
                // Found a matching site
                displaySearchResults(data.results[0]);
            } else {
                // No results found
                document.getElementById('searchResults').innerHTML = '<p>No sites found matching your search.</p>';
            }
        } catch (error) {
            console.error("Search error:", error);
            document.getElementById('searchResults').innerHTML = `<p>Error: ${error.message}</p>`;
        }
    }

    function displaySearchResults(site) {
        console.log("Found site:", site);

        // Display basic info in search results
        document.getElementById('searchResults').innerHTML = `
            <div class="search-result">
                <p><strong>Site ID:</strong> ${site.site_id}</p>
                <p><strong>Store Name:</strong> ${site.store_name || 'N/A'}</p>
                <p><strong>Region:</strong> ${site.region || 'N/A'}</p>
                <button id="viewDetailsBtn" class="btn btn-primary">View Details</button>
            </div>
        `;

        // Add event listener to the view details button
        document.getElementById('viewDetailsBtn').addEventListener('click', async () => {
            if (!site.site_id) {
                console.error("Cannot load site details: site_id is missing");
                alert("Error: Cannot load site details due to missing site ID");
                return;
            }

            loadSiteDetails(site.site_id);
        });
    }

    async function loadSiteDetails(siteId) {
        try {
            if (!siteId) {
                console.error("Cannot load site details: No site ID provided");
                alert("Error: No site ID provided");
                return;
            }

            console.log(`Loading details for site ID: ${siteId}`);
            document.getElementById('siteDetails').innerHTML = '<p>Loading site details...</p>';

            const data = await makeAuthenticatedRequest(`/api/sites?site_id=${encodeURIComponent(siteId)}`);

            if (data.error) {
                document.getElementById('siteDetails').innerHTML = `<p>Error: ${data.message || 'Failed to load site data'}</p>`;
                return;
            }

            console.log("*** Site details raw response:", data);
            console.log("*** Response type:", typeof data);
            console.log("*** Keys in response:", Object.keys(data));

            if (typeof data === 'object' && data !== null) {
                console.log("*** Example values:", {
                    site: data.site,
                    site_id: data.site_id,
                    store_name: data.store_name,
                    region: data.region,
                    div: data.div,
                    present_rent: data.present_rent
                });
            }

            // Update the site data in the card view first
            updateSiteData(data);

            // Then render the detailed view
            renderSiteDetails(data);
        } catch (error) {
            console.error("Error loading site details:", error);
            document.getElementById('siteDetails').innerHTML = `<p>Error loading site details: ${error.message}</p>`;
        }
    }

    // Add event listener for the search form
    document.getElementById('searchForm').addEventListener('submit', function(event) {
        event.preventDefault();
        searchSite();
    });

    function renderSiteDetails(response) {
        try {
            console.log("Rendering site details:", response);
            const siteDetails = document.getElementById('siteDetails');

            // Check if we have valid site data
            if (!response) {
                siteDetails.innerHTML = '<p>No site data available.</p>';
                return;
            }

            // Extract site data from the response - handle different possible formats
            let siteData = response;

            // Display the data on the card view as well
            populateDataGridCards(siteData);

            // Clear previous content and create a container
            siteDetails.innerHTML = '';
            const detailsContainer = document.createElement('div');
            detailsContainer.className = 'site-details-container';

            // Create a header section
            const header = document.createElement('div');
            header.className = 'site-details-header';

            // Determine the values to display in the header
            const siteName = siteData.site_id || siteData.site || 'N/A';
            const storeName = siteData.store_name || 'Unknown Store';
            const region = siteData.region || 'N/A';
            const division = siteData.division || siteData.div || 'N/A';

            header.innerHTML = `
                <h2>${storeName}</h2>
                <div class="site-id">Site ID: ${siteName}</div>
                <div class="site-region">${region} / ${division}</div>
            `;
            detailsContainer.appendChild(header);

            // Create the main details grid
            const detailsGrid = document.createElement('div');
            detailsGrid.className = 'site-details-grid';

            // Define the sections and their fields
            const sections = [
                {
                    title: 'Basic Information',
                    fields: [
                        { key: 'site_id', label: 'Site ID' },
                        { key: 'site', label: 'Site' },
                        { key: 'store_name', label: 'Store Name' },
                        { key: 'region', label: 'Region' },
                        { key: 'division', label: 'Division' },
                        { key: 'div', label: 'Division' },
                        { key: 'status', label: 'Status' },
                        { key: 'manager', label: 'Manager' },
                        { key: 'asst_manager', label: 'Asst. Manager' },
                        { key: 'executive', label: 'Executive' }
                    ]
                },
                {
                    title: 'Lease Information',
                    fields: [
                        { key: 'doo', label: 'DOO' },
                        { key: 'sqft', label: 'Sq. Ft.' },
                        { key: 'agreement_date', label: 'Agreement Date' },
                        { key: 'rent_position_date', label: 'Rent Position Date' },
                        { key: 'rent_effective_date', label: 'Rent Effective Date' },
                        { key: 'agreement_valid_upto', label: 'Agreement Valid Upto' },
                        { key: 'current_date', label: 'Current Date' },
                        { key: 'lease_period', label: 'Lease Period' },
                        { key: 'RENT FREE PERIOD DAYS', label: 'Rent Free Period (Days)' },
                        { key: 'rent_effective_amount', label: 'Rent Effective Amount' },
                        { key: 'present_rent', label: 'Present Rent' },
                        { key: 'hike_percentage', label: 'Hike Percentage' },
                        { key: 'hike_year', label: 'Hike Year' },
                        { key: 'rent_deposit', label: 'Rent Deposit' }
                    ]
                },
                {
                    title: 'Owner Information',
                    fields: [
                        { key: 'owner_name1', label: 'Owner Name 1' },
                        { key: 'owner_name2', label: 'Owner Name 2' },
                        { key: 'owner_name3', label: 'Owner Name 3' },
                        { key: 'owner_name4', label: 'Owner Name 4' },
                        { key: 'owner_name5', label: 'Owner Name 5' },
                        { key: 'owner_name6', label: 'Owner Name 6' },
                        { key: 'owner_mobile', label: 'Owner Mobile' },
                        { key: 'gst_number', label: 'GST Number' },
                        { key: 'pan_number', label: 'PAN NUMBER' },
                        { key: 'tds_percentage', label: 'TDS_PERCENTAGE' }
                    ]
                },
                {
                    title: 'Additional Information',
                    fields: [
                        { key: 'current_date1', label: 'Current Date 1' },
                        { key: 'validity_date', label: 'Validity Date' },
                        { key: 'mature', label: 'Mature' },
                        { key: 'remarks', label: 'Remarks' }
                    ]
                }
            ];

            // Populate each section
            sections.forEach(section => {
                const sectionElement = document.createElement('div');
                sectionElement.className = 'details-section';

                // Add section title
                const sectionTitle = document.createElement('h3');
                sectionTitle.textContent = section.title;
                sectionElement.appendChild(sectionTitle);

                // Add fields
                const fieldsContainer = document.createElement('div');
                fieldsContainer.className = 'fields-container';

                section.fields.forEach(field => {
                    const fieldElement = document.createElement('div');
                    fieldElement.className = 'field';

                    const label = document.createElement('div');
                    label.className = 'field-label';
                    label.textContent = field.label;

                    const value = document.createElement('div');
                    value.className = 'field-value';

                    // Format the value based on its type
                    let displayValue = siteData[field.key];

                    // Handle special cases
                    if (field.key === 'present_rent' || field.key === 'security_deposit') {
                        displayValue = displayValue ? formatCurrency(displayValue) : 'N/A';
                    } else if (field.key === 'hike_percentage') {
                        displayValue = displayValue ? `${displayValue}%` : 'N/A';
                    } else {
                        displayValue = displayValue || 'N/A';
                    }

                    value.textContent = displayValue;

                    fieldElement.appendChild(label);
                    fieldElement.appendChild(value);
                    fieldsContainer.appendChild(fieldElement);
                });

                sectionElement.appendChild(fieldsContainer);
                detailsGrid.appendChild(sectionElement);
            });

            detailsContainer.appendChild(detailsGrid);
            siteDetails.appendChild(detailsContainer);

            // Also populate the data grid cards (existing elements in HTML)
            populateDataGridCards(siteData);

        } catch (error) {
            console.error("Error rendering site details:", error);
            document.getElementById('siteDetails').innerHTML = `<p>Error rendering site details: ${error.message}</p>`;
        }
    }

    function populateDataGridCards(siteData) {
        console.log("Populating data grid cards with:", siteData);

        if (!siteData) {
            console.error("No site data provided to populateDataGridCards");
            return;
        }

        // Map of field IDs to their corresponding data keys
        const fieldMapping = {
            'site_value': ['SITE', 'site', 'site_id'],
            'store_name_value': ['STORE NAME', 'store_name'],
            'region_value': ['REGION', 'region'],
            'div_value': ['DIV', 'div'],
            'manager_value': ['MANAGER', 'manager'],
            'asst_manager_value': ['ASST MANAGER', 'asst_manager'],
            'executive_value': ['EXECUTIVE', 'executive'],
            'doo_value': ['D.O.O', 'doo'],
            'sqft_value': ['SQ.FT', 'sqft'],
            'agreement_date_value': ['AGREEMENT DATE', 'agreement_date'],
            'rent_position_date_value': ['RENT POSITION DATE', 'rent_position_date'],
            'rent_effective_date_value': ['RENT EFFECTIVE DATE', 'rent_effective_date'],
            'agreement_valid_upto_value': ['AGREEMENT VALID UPTO', 'agreement_valid_upto'],
            'current_date_value': ['CURRENT DATE', 'current_date'],
            'lease_period_value': ['LEASE PERIOD', 'lease_period'],
            'rent_free_period_days_value': ['RENT FREE PERIOD DAYS', 'rent_free_period_days'],
            'rent_effective_amount_value': ['RENT EFFECTIVE AMOUNT', 'rent_effective_amount'],
            'present_rent_value': ['PRESENT RENT', 'present_rent'],
            'hike_percentage_value': ['HIKE %', 'hike_percentage'],
            'hike_year_value': ['HIKE YEAR', 'hike_year'],
            'rent_deposit_value': ['RENT DEPOSIT', 'rent_deposit'],
            'owner_name1_value': ['OWNER NAME-1', 'owner_name1'],
            'owner_name2_value': ['OWNER NAME-2', 'owner_name2'],
            'owner_name3_value': ['OWNER NAME-3', 'owner_name3'],
            'owner_name4_value': ['OWNER NAME-4', 'owner_name4'],
            'owner_name5_value': ['OWNER NAME-5', 'owner_name5'],
            'owner_name6_value': ['OWNER NAME-6', 'owner_name6'],
            'owner_mobile_value': ['OWNER MOBILE', 'owner_mobile'],
            'current_date1_value': ['CURRENT DATE 1', 'current_date1'],
            'validity_date_value': ['VALIDITY DATE', 'validity_date'],
            'gst_number_value': ['GST NUMBER', 'gst_number'],
            'pan_number_value': ['PAN NUMBER', 'pan_number'],
            'tds_percentage_value': ['TDS PERCENTAGE', 'tds_percentage'],
            'mature_value': ['MATURE', 'mature'],
            'status_value': ['STATUS', 'status'],
            'remarks_value': ['REMARKS', 'remarks']
        };

        // Helper function to get value from data with multiple potential field names
        function getFieldValue(data, fieldNames) {
            for (const fieldName of fieldNames) {
                if (data[fieldName] !== undefined && data[fieldName] !== null && data[fieldName] !== '') {
                    return data[fieldName];
                }
            }
            return null;
        }

        // Populate each field if it exists in the DOM
        for (const [elementId, dataKeys] of Object.entries(fieldMapping)) {
            const element = document.getElementById(elementId);
            if (element) {
                console.log(`Looking for ${dataKeys.join('/')} in siteData to populate ${elementId}`);

                // Get the value from site data using our helper function
                let value = getFieldValue(siteData, dataKeys);

                // Format the value based on its type
                if (elementId === 'present_rent_value' || elementId === 'rent_deposit_value' || elementId === 'rent_effective_amount_value') {
                    value = value ? formatCurrency(value) : 'N/A';
                } else if (elementId === 'hike_percentage_value' || elementId === 'tds_percentage_value') {
                    if (value) {
                        try {
                            if (typeof value === 'string') value = parseFloat(value);
                            if (!isNaN(value)) value = value + '%';
                        } catch (e) {
                            console.error(`Error formatting ${elementId}:`, e);
                        }
                    } else {
                        value = 'N/A';
                    }
                } else {
                    value = value || 'N/A';
                }

                console.log(`Setting ${elementId} to:`, value);
                element.textContent = value;
            }
        }
    }

    // Load initial site data
    async function loadInitialSiteData() {
        try {
            // Get a default site to display
            const data = await makeAuthenticatedRequest(`/api/search?term=SITE001&site_id_search=true`);

            if (data.error) {
                console.log("No initial site data found:", data.message);
                return;
            }

            if (data.results && data.results.length > 0) {
                const site = data.results[0];
                console.log("Loading initial site:", site.site_id);
                await loadSiteDetails(site.site_id);
            }
        } catch (error) {
            console.error("Error loading initial site data:", error);
        }
    }

    // Load initial data when page loads
    loadInitialSiteData();

    // Add this function to handle sidebar menu setup
    function setupSidebarMenu() {
        // Get all menu items
        const menuItems = document.querySelectorAll('.sidebar-menu li a');

        // Set initial state - only Dashboard is selected by default
        menuItems.forEach(item => {
            item.classList.remove('selected');
        });

        // Set Dashboard as selected by default
        const dashboardLink = document.getElementById('dashboardLink');
        if (dashboardLink) {
            dashboardLink.classList.add('selected');
        }

        // Add click event listeners to all sidebar menu links
        menuItems.forEach(item => {
            item.addEventListener('click', function(e) {
                // Remove 'selected' class from all links
                menuItems.forEach(link => {
                    link.classList.remove('selected');
                });

                // Add 'selected' class to the clicked link
                this.classList.add('selected');
            });
        });
    }
});