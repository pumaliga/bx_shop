document.addEventListener('DOMContentLoaded', function() {
    const citySelect = document.querySelector('[name="city"]');
    const deliveryProviderSelect = document.querySelector('[name="delivery_provider"]');
    const deliveryTypeSelect = document.querySelector('[name="delivery_type"]');

    const searchInput = document.getElementById('warehouse-search');
    const optionsList = document.getElementById('warehouse-options');
    const streetAutocompleteInput = document.getElementById('street-autocomplete');
    const streetOptionsList = document.getElementById('street-options');
    const streetAutocompleteWrapper = document.getElementById('street-autocomplete-wrapper');

    const streetField = document.getElementById('id_street').closest('p');
    const houseNumberField = document.getElementById('id_house_number').closest('p');
    const flatNumberField = document.getElementById('id_flat_number').closest('p');
    const warehouseWrapper = document.getElementById('warehouse-wrapper');

    let warehouses = [];
    let warehouseSelected = false;
    let streetSelected = false;
    let cityValidated = false;

    function filterWarehouses(query) {
        const lowerQuery = query.toLowerCase();
        return warehouses.filter(w => w.Description.toLowerCase().includes(lowerQuery));
    }

    function renderOptions(filteredWarehouses) {
        optionsList.innerHTML = '';

        filteredWarehouses.forEach(warehouse => {
            const li = document.createElement('li');
            li.textContent = warehouse.Description;
            li.dataset.ref = warehouse.Ref;
            optionsList.appendChild(li);
        });

        optionsList.classList.toggle('hidden', filteredWarehouses.length === 0);
    }

    // Store ref and mark as selected
    optionsList.addEventListener('click', (e) => {
        if (e.target.tagName === 'LI') {
            const selectedOption = e.target;
            searchInput.value = selectedOption.textContent;
            optionsList.classList.add('hidden');
            warehouseSelected = true;
            
            // Update hidden form field
            document.getElementById('id_warehouse_description').value = selectedOption.textContent;
        }
    });

    searchInput.addEventListener('input', () => {
        warehouseSelected = false;  // User is typing again
        document.getElementById('id_warehouse_description').value = '';
        const filtered = filterWarehouses(searchInput.value);
        renderOptions(filtered);
    });

    searchInput.addEventListener('focus', () => {
        warehouseSelected = false;  // User is focusing again (starting new interaction)
        const filtered = filterWarehouses(searchInput.value);
        renderOptions(filtered);
    });

    document.addEventListener('click', (e) => {
        if (!e.target.closest('.custom-select-wrapper')) {
            optionsList.classList.add('hidden');
            streetOptionsList.classList.add('hidden');

            // Only clear if nothing has been selected
            if (!warehouseSelected) {
                searchInput.value = '';
                document.getElementById('id_warehouse_description').value = '';
            }

            // Only clear street if nothing has been selected
            if (!streetSelected) {
                streetAutocompleteInput.value = '';
                document.getElementById('id_street').value = '';
            }
        }
    });

    function updateDeliveryFields() {
        const deliveryProvider = deliveryProviderSelect.value;
        const deliveryType = deliveryTypeSelect.value;
        const city = document.getElementById('id_city').value.trim();

        const isBranchDelivery = deliveryType === 'branch';
        const isCourierDelivery = deliveryType === 'courier';
        const isNovaPoshtaBranch = isBranchDelivery && deliveryProvider === 'nova_poshta';
        const isNovaPoshtaCourier = isCourierDelivery && deliveryProvider === 'nova_poshta';

        // Show/hide address fields for courier
        streetField.style.display = 'none'; // Hide original street field
        houseNumberField.style.display = isCourierDelivery ? 'block' : 'none';
        flatNumberField.style.display = isCourierDelivery ? 'block' : 'none';
        
        // Show street autocomplete for Nova Poshta courier
        streetAutocompleteWrapper.style.display = isNovaPoshtaCourier ? 'block' : 'none';

        // Show/hide warehouse UI
        warehouseWrapper.style.display = isNovaPoshtaBranch ? 'block' : 'none';

        // Handle warehouse fields
        if (!isNovaPoshtaBranch) {
            searchInput.disabled = true;
            searchInput.value = '';
            document.getElementById('id_warehouse_description').value = '';
            optionsList.innerHTML = '';
            warehouseSelected = false;
        } else {
            if (city) {
                loadNovaPoshtaWarehouses(city);
            } else {
                searchInput.disabled = true;
            }
        }

        // Handle courier fields - validate city first for Nova Poshta
        if (isCourierDelivery) {
            const houseInput = document.getElementById('id_house_number');
            const flatInput = document.getElementById('id_flat_number');
            
            if (!city) {
                // Disable courier fields when no city
                if (isNovaPoshtaCourier) {
                    streetAutocompleteInput.disabled = true;
                    streetOptionsList.innerHTML = '';
                    cityValidated = false;
                }
                houseInput.disabled = true;
                flatInput.disabled = true;
            } else {
                // For Nova Poshta courier, validate city first
                if (isNovaPoshtaCourier) {
                    validateCityForCourier(city);
                } else {
                    // For other providers, enable fields directly
                    houseInput.disabled = false;
                    flatInput.disabled = false;
                    houseInput.placeholder = 'House number';
                    flatInput.placeholder = 'Flat number';
                }
            }
        }
    }

    deliveryProviderSelect.addEventListener('change', updateDeliveryFields);
    deliveryTypeSelect.addEventListener('change', updateDeliveryFields);
    citySelect.addEventListener('input', updateDeliveryFields);

    // Initial run
    updateDeliveryFields();

    function loadNovaPoshtaWarehouses(city) {
        if (!city || deliveryProviderSelect.value !== 'nova_poshta' || deliveryTypeSelect.value !== 'branch') {
            searchInput.disabled = true;
            searchInput.value = '';
            optionsList.innerHTML = '';
            return;
        }

        fetch(`/orders/get-nova-poshta-warehouses/?city=${encodeURIComponent(city)}`)
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    searchInput.disabled = true;
                    warehouses = [];
                    optionsList.innerHTML = '';
                    return;
                }
                
                if (!Array.isArray(data)) {
                    console.error('Unexpected response:', data);
                    return;
                }

                warehouses = data;
                searchInput.disabled = false;
                searchInput.placeholder = 'Select a warehouse...';
                searchInput.value = '';
                document.getElementById('id_warehouse_description').value = '';
                optionsList.innerHTML = '';
                warehouseSelected = false;
            })
            .catch(error => {
                console.error('Error loading warehouses:', error);
                searchInput.disabled = true;
                searchInput.placeholder = 'Failed to load warehouses';
            });
    }

    function validateCityForCourier(city) {
        if (!city) {
            streetAutocompleteInput.disabled = true;
            cityValidated = false;
            return;
        }

        fetch(`/orders/validate-city/?city=${encodeURIComponent(city)}`)
            .then(response => response.json())
            .then(data => {
                const houseInput = document.getElementById('id_house_number');
                const flatInput = document.getElementById('id_flat_number');
                
                if (data.error) {
                    streetAutocompleteInput.disabled = true;
                    streetAutocompleteInput.placeholder = 'City must be valid first';
                    houseInput.disabled = true;
                    flatInput.disabled = true;
                    cityValidated = false;
                    return;
                }
                
                // City is valid, enable courier fields
                streetAutocompleteInput.disabled = false;
                streetAutocompleteInput.placeholder = 'Start typing street name...';
                houseInput.disabled = false;
                flatInput.disabled = false;
                houseInput.placeholder = 'House number';
                flatInput.placeholder = 'Flat number';
                cityValidated = true;
            })
            .catch(error => {
                console.error('Error validating city:', error);
                streetAutocompleteInput.disabled = true;
                streetAutocompleteInput.placeholder = 'Failed to validate city';
                cityValidated = false;
            });
    }

    // Note: citySelect.addEventListener('input') is already handled in updateDeliveryFields above
    deliveryProviderSelect.addEventListener('change', () => loadNovaPoshtaWarehouses(citySelect.value));
    deliveryTypeSelect.addEventListener('change', () => loadNovaPoshtaWarehouses(citySelect.value));

    // Street autocomplete functionality
    function searchStreets(query) {
        if (query.length < 2 || deliveryProviderSelect.value !== 'nova_poshta' || deliveryTypeSelect.value !== 'courier') {
            streetOptionsList.innerHTML = '';
            streetOptionsList.classList.add('hidden');
            return;
        }

        // Check if city is validated first
        if (!cityValidated) {
            streetOptionsList.innerHTML = '';
            streetOptionsList.classList.add('hidden');
            return;
        }

        fetch(`/orders/get-search-streets/?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    streetOptionsList.innerHTML = '';
                    streetOptionsList.classList.add('hidden');
                    return;
                }

                streetOptionsList.innerHTML = '';
                data.forEach(street => {
                    const li = document.createElement('li');
                    li.textContent = street.label;
                    li.dataset.ref = street.ref;
                    streetOptionsList.appendChild(li);
                });

                streetOptionsList.classList.toggle('hidden', data.length === 0);
            })
            .catch(error => {
                console.error('Error loading streets:', error);
                streetOptionsList.innerHTML = '';
                streetOptionsList.classList.add('hidden');
            });
    }

    // Street selection
    streetOptionsList.addEventListener('click', (e) => {
        if (e.target.tagName === 'LI') {
            const selectedStreet = e.target;
            streetAutocompleteInput.value = selectedStreet.textContent;
            document.getElementById('id_street').value = selectedStreet.textContent;
            streetOptionsList.classList.add('hidden');
            streetSelected = true;
        }
    });

    streetAutocompleteInput.addEventListener('input', () => {
        console.log('Street input changed:', streetAutocompleteInput.value);
        console.log('Query length:', streetAutocompleteInput.value.length);
        console.log('Delivery provider:', deliveryProviderSelect.value);
        console.log('Delivery type:', deliveryTypeSelect.value);
        console.log('City value:', citySelect.value);
        
        streetSelected = false;
        document.getElementById('id_street').value = '';
        searchStreets(streetAutocompleteInput.value);
    });

    // Initial load
    if (citySelect.value) {
        loadNovaPoshtaWarehouses(citySelect.value);
    }
});