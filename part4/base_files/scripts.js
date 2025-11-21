/* 
  HBnB Part 4 - Client-Side JavaScript
  This file handles all client-side functionality including authentication,
  place listings, place details, and reviews.
*/

// Configuration de l'API
const API_BASE_URL = 'http://127.0.0.1:5000/api/v1';

// Utilitaires pour la gestion des cookies
const CookieManager = {
    /**
     * Définir un cookie
     * @param {string} name - Nom du cookie
     * @param {string} value - Valeur du cookie
     * @param {number} days - Durée de vie en jours (optionnel)
     */
    setCookie: (name, value, days = 7) => {
        let expires = "";
        if (days) {
            const date = new Date();
            date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
            expires = `; expires=${date.toUTCString()}`;
        }
        document.cookie = `${name}=${value || ""}${expires}; path=/`;
    },

    /**
     * Récupérer un cookie
     * @param {string} name - Nom du cookie
     * @returns {string|null} - Valeur du cookie ou null
     */
    getCookie: (name) => {
        const nameEQ = `${name}=`;
        const cookies = document.cookie.split(';');
        
        for (let i = 0; i < cookies.length; i++) {
            let cookie = cookies[i].trim();
            if (cookie.indexOf(nameEQ) === 0) {
                return cookie.substring(nameEQ.length, cookie.length);
            }
        }
        return null;
    },

    /**
     * Supprimer un cookie
     * @param {string} name - Nom du cookie
     */
    deleteCookie: (name) => {
        document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`;
    }
};

// ========================================
// AUTHENTIFICATION - LOGIN
// ========================================

/**
 * Connexion de l'utilisateur via l'API
 * @param {string} email - Email de l'utilisateur
 * @param {string} password - Mot de passe de l'utilisateur
 * @returns {Promise<Object>} - Réponse de l'API
 */
async function loginUser(email, password) {
    try {
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, password })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || 'Login failed');
        }

        return await response.json();
    } catch (error) {
        console.error('Login error:', error);
        throw error;
    }
}

/**
 * Vérifier si l'utilisateur est connecté
 * @returns {boolean} - True si connecté, false sinon
 */
function isAuthenticated() {
    return CookieManager.getCookie('token') !== null;
}

/**
 * Déconnexion de l'utilisateur
 */
function logoutUser() {
    CookieManager.deleteCookie('token');
    window.location.href = 'login.html';
}

/**
 * Obtenir le token JWT
 * @returns {string|null} - Token JWT ou null
 */
function getAuthToken() {
    return CookieManager.getCookie('token');
}

// ========================================
// GESTION DE LA PAGE LOGIN
// ========================================

function initLoginPage() {
    const loginForm = document.getElementById('login-form');
    const errorMessage = document.getElementById('error-message');

    if (loginForm) {
        loginForm.addEventListener('submit', async (event) => {
            event.preventDefault();

            // Récupérer les valeurs du formulaire
            const email = document.getElementById('email').value.trim();
            const password = document.getElementById('password').value.trim();

            // Validation basique
            if (!email || !password) {
                showMessage(errorMessage, 'Please enter both email and password.', 'error');
                return;
            }

            try {
                // Afficher un indicateur de chargement (optionnel)
                const submitButton = loginForm.querySelector('button[type="submit"]');
                const originalText = submitButton.textContent;
                submitButton.textContent = 'Logging in...';
                submitButton.disabled = true;

                // Appel à l'API
                const data = await loginUser(email, password);

                // Stocker le token dans un cookie
                CookieManager.setCookie('token', data.access_token, 7); // 7 jours

                // Redirection vers la page principale
                window.location.href = 'index.html';

            } catch (error) {
                // Afficher le message d'erreur
                showMessage(errorMessage, `Login failed: ${error.message}`, 'error');
                
                // Réactiver le bouton
                const submitButton = loginForm.querySelector('button[type="submit"]');
                submitButton.textContent = 'Login';
                submitButton.disabled = false;
            }
        });
    }
}

/**
 * Afficher un message dans un élément
 * @param {HTMLElement} element - Élément HTML où afficher le message
 * @param {string} message - Message à afficher
 * @param {string} type - Type de message ('error' ou 'success')
 */
function showMessage(element, message, type) {
    if (element) {
        element.textContent = message;
        element.className = `form-message ${type}`;
        element.style.display = 'block';

        // Masquer le message après 5 secondes
        setTimeout(() => {
            element.style.display = 'none';
        }, 5000);
    }
}

// ========================================
// GESTION DE LA PAGE INDEX (Liste des lieux)
// ========================================

function initIndexPage() {
    // Vérifier si l'utilisateur est connecté
    checkAuthentication();

    // Charger la liste des lieux
    fetchPlaces();

    // Gérer le bouton de connexion/déconnexion
    updateLoginButton();

    // Initialiser le filtrage par prix
    initPriceFilter();
}

/**
 * Vérifier l'authentification et rediriger si nécessaire
 */
function checkAuthentication() {
    const token = getAuthToken();
    
    // Si on est sur une page protégée et pas de token
    const currentPage = window.location.pathname.split('/').pop();
    const protectedPages = ['add_review.html'];
    
    if (protectedPages.includes(currentPage) && !token) {
        window.location.href = 'index.html';
    }
}

/**
 * Mettre à jour le bouton de connexion/déconnexion
 */
function updateLoginButton() {
    const loginLink = document.getElementById('login-link');
    
    if (loginLink) {
        if (isAuthenticated()) {
            loginLink.textContent = 'Logout';
            loginLink.href = '#';
            loginLink.addEventListener('click', (e) => {
                e.preventDefault();
                logoutUser();
            });
        } else {
            loginLink.textContent = 'Login';
            loginLink.href = 'login.html';
        }
    }
}

/**
 * Récupérer la liste des lieux depuis l'API
 */
async function fetchPlaces() {
    try {
        const token = getAuthToken();
        const headers = {
            'Content-Type': 'application/json'
        };

        // Ajouter le token si disponible
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        const response = await fetch(`${API_BASE_URL}/places/`, {
            method: 'GET',
            headers: headers
        });

        if (!response.ok) {
            throw new Error('Failed to fetch places');
        }

        const places = await response.json();
        displayPlaces(places);

    } catch (error) {
        console.error('Error fetching places:', error);
        const placesList = document.getElementById('places-list');
        if (placesList) {
            placesList.innerHTML = '<p style="text-align: center; color: #e74c3c;">Failed to load places. Please try again later.</p>';
        }
    }
}

/**
 * Afficher la liste des lieux
 * @param {Array} places - Liste des lieux
 */
function displayPlaces(places) {
    const placesList = document.getElementById('places-list');
    
    if (!placesList) return;

    // Vider la liste
    placesList.innerHTML = '';

    if (places.length === 0) {
        placesList.innerHTML = '<p style="text-align: center;">No places available.</p>';
        return;
    }

    // Créer une carte pour chaque lieu
    places.forEach(place => {
        const placeCard = createPlaceCard(place);
        placesList.appendChild(placeCard);
    });
}

/**
 * Initialiser le filtrage par prix
 */
function initPriceFilter() {
  const priceFilter = document.getElementById('price-filter');
  
  if (!priceFilter) return;
  
  priceFilter.addEventListener('change', (event) => {
      const maxPrice = event.target.value;
      const placeCards = document.querySelectorAll('.place-card');
      
      placeCards.forEach(card => {
          if (!maxPrice) {
              // "All" sélectionné - afficher tous les lieux
              card.style.display = 'block';
              return;
          }
          
          // Récupère le prix depuis la carte
          const priceElement = card.querySelector('.price');
          if (priceElement) {
              // Extrait le nombre du texte "150€ per night"
              const priceText = priceElement.textContent;
              const price = parseFloat(priceText.replace(/[^0-9.]/g, ''));
              
              // Filtre selon le prix sélectionné
              if (price <= parseFloat(maxPrice)) {
                  card.style.display = 'block';
              } else {
                  card.style.display = 'none';
              }
          }
      });
  });
}

/**
 * Créer une carte pour un lieu
 * @param {Object} place - Données du lieu
 * @returns {HTMLElement} - Élément HTML de la carte
 */
function createPlaceCard(place) {
  const card = document.createElement('div');
  card.className = 'place-card';

  // Images différentes selon le titre
  let imageUrl = 'images/Places1.jpg';
  
  const title = (place.title || '').toLowerCase();
  
  if (title.includes('villa') || title.includes('luxury')) {
      imageUrl = 'https://images.unsplash.com/photo-1613490493576-7fde63acd811?w=600&auto=format&q=85';
  } else if (title.includes('beach') || title.includes('ocean') || title.includes('house')) {
      imageUrl = 'https://images.unsplash.com/photo-1499793983690-e29da59ef1c2?w=600&auto=format&q=85';
  } else if (title.includes('mountain') || title.includes('cabin')) {
      imageUrl = 'https://images.unsplash.com/photo-1759344448782-87472a4f7c22?w=600&auto=format&q=85';
  } else if (title.includes('apartment') || title.includes('city')) {
      imageUrl = 'https://images.unsplash.com/photo-1502672260066-6bc885565d89?w=600&auto=format&q=85';
  }

  card.innerHTML = `
      <img src="${imageUrl}" alt="${place.title || 'Place'}">
      <div class="place-info">
          <h3>${place.title || 'Unnamed Place'}</h3>
          <p class="price">${place.price || 0}€ per night</p>
          <button class="details-button" onclick="viewPlaceDetails('${place.id}')">View Details</button>
      </div>
  `;

  return card;
}

/**
 * Rediriger vers la page de détails d'un lieu
 * @param {string} placeId - ID du lieu
 */
function viewPlaceDetails(placeId) {
    window.location.href = `place.html?id=${placeId}`;
}

// ========================================
// GESTION DE LA PAGE PLACE DETAILS
// ========================================

function initPlaceDetailsPage() {
    // Récupérer l'ID du lieu depuis l'URL
    const urlParams = new URLSearchParams(window.location.search);
    const placeId = urlParams.get('id');

    if (placeId) {
        fetchPlaceDetails(placeId);
    } else {
        // Rediriger vers l'index si pas d'ID
        window.location.href = 'index.html';
    }

    // Mettre à jour le bouton de connexion
    updateLoginButton();

    // Afficher/masquer le bouton d'ajout d'avis selon l'authentification
    toggleAddReviewButton();
}

/**
 * Afficher/masquer le bouton d'ajout d'avis
 */
function toggleAddReviewButton() {
    const addReviewSection = document.getElementById('add-review-section');
    
    if (addReviewSection) {
        if (isAuthenticated()) {
            addReviewSection.style.display = 'block';
            
            // Ajouter l'ID du lieu au lien
            const urlParams = new URLSearchParams(window.location.search);
            const placeId = urlParams.get('id');
            const addReviewButton = addReviewSection.querySelector('.add-review-button');
            
            if (addReviewButton && placeId) {
                addReviewButton.href = `add_review.html?place_id=${placeId}`;
            }
        } else {
            addReviewSection.style.display = 'none';
        }
    }
}

/**
 * Récupérer les détails d'un lieu
 * @param {string} placeId - ID du lieu
 */
async function fetchPlaceDetails(placeId) {
    try {
        const token = getAuthToken();
        const headers = {
            'Content-Type': 'application/json'
        };

        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        const response = await fetch(`${API_BASE_URL}/places/${placeId}`, {
            method: 'GET',
            headers: headers
        });

        if (!response.ok) {
            throw new Error('Failed to fetch place details');
        }

        const place = await response.json();
        displayPlaceDetails(place);
        
        // Charger les avis pour ce lieu
        fetchPlaceReviews(placeId);

    } catch (error) {
        console.error('Error fetching place details:', error);
        const placeDetails = document.getElementById('place-details');
        if (placeDetails) {
            placeDetails.innerHTML = '<p style="color: #e74c3c;">Failed to load place details.</p>';
        }
    }
}

/**
 * Afficher les détails d'un lieu
 * @param {Object} place - Données du lieu
 */
function displayPlaceDetails(place) {
    // Mettre à jour le titre
    const titleElement = document.getElementById('place-title');
    if (titleElement) {
        titleElement.textContent = place.title || 'Unnamed Place';
    }

    // Mettre à jour la localisation
    const locationElement = document.querySelector('.place-location');
    if (locationElement && place.city && place.country) {
        locationElement.textContent = `📍 ${place.city}, ${place.country}`;
    }

    // Mettre à jour l'image
    const imageElement = document.getElementById('place-img');
    if (imageElement) {
        let imageUrl = 'images/Places1.jpg';
        const title = (place.title || '').toLowerCase();
        
        if (title.includes('villa') || title.includes('luxury')) {
            imageUrl = 'https://images.unsplash.com/photo-1613490493576-7fde63acd811?w=1200&auto=format&q=85';
        } else if (title.includes('beach') || title.includes('ocean') || title.includes('house')) {
            imageUrl = 'https://images.unsplash.com/photo-1499793983690-e29da59ef1c2?w=1200&auto=format&q=85';
        } else if (title.includes('mountain') || title.includes('cabin')) {
            imageUrl = 'https://images.unsplash.com/photo-1759344448782-87472a4f7c22?w=1200&auto=format&q=85';
        } else if (title.includes('apartment') || title.includes('city')) {
            imageUrl = 'https://images.unsplash.com/photo-1502672260066-6bc885565d89?w=1200&auto=format&q=85';
        }
        
        imageElement.src = imageUrl;
        imageElement.alt = place.title || 'Place';
    }

    // Mettre à jour la description
    const descriptionElement = document.getElementById('place-description');
    if (descriptionElement) {
        descriptionElement.textContent = place.description || 'No description available.';
    }

    // Mettre à jour l'hôte
    const hostElement = document.getElementById('place-host');
    if (hostElement) {
      // L'API retourne place.owner avec first_name et last_name
      if (place.owner) {
          hostElement.textContent = `${place.owner.first_name} ${place.owner.last_name}`;
      } else {
          hostElement.textContent = 'Unknown';
      }
  }

    // Mettre à jour le prix
    const priceElement = document.getElementById('place-price');
    if (priceElement) {
        priceElement.textContent = `${place.price || 0}€`;
    }

    // Mettre à jour les équipements (amenities)
    displayAmenities(place.amenities);
}

/**
 * Afficher les équipements
 * @param {Array} amenities - Liste des équipements
 */
function displayAmenities(amenities) {
    const amenitiesElement = document.getElementById('place-amenities');
    
    if (!amenitiesElement) return;

    if (!amenities || amenities.length === 0) {
        amenitiesElement.innerHTML = '<p>No amenities listed.</p>';
        return;
    }

    amenitiesElement.innerHTML = '';
    
    amenities.forEach(amenity => {
        const amenityItem = document.createElement('span');
        amenityItem.className = 'amenity-item';
        amenityItem.textContent = amenity.name || amenity;
        amenitiesElement.appendChild(amenityItem);
    });
}

/**
 * Récupérer les avis pour un lieu
 * @param {string} placeId - ID du lieu
 */
async function fetchPlaceReviews(placeId) {
    try {
        const response = await fetch(`${API_BASE_URL}/places/${placeId}/reviews/`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error('Failed to fetch reviews');
        }

        const reviews = await response.json();
        displayReviews(reviews);

    } catch (error) {
        console.error('Error fetching reviews:', error);
        const reviewsList = document.getElementById('reviews-list');
        if (reviewsList) {
            reviewsList.innerHTML = '<p>No reviews yet.</p>';
        }
    }
}

/**
 * Afficher les avis
 * @param {Array} reviews - Liste des avis
 */
function displayReviews(reviews) {
    const reviewsList = document.getElementById('reviews-list');
    
    if (!reviewsList) return;

    reviewsList.innerHTML = '';

    if (reviews.length === 0) {
        reviewsList.innerHTML = '<p>No reviews yet. Be the first to review!</p>';
        return;
    }

    reviews.forEach(review => {
        const reviewCard = createReviewCard(review);
        reviewsList.appendChild(reviewCard);
    });
}

/**
 * Créer une carte pour un avis
 * @param {Object} review - Données de l'avis
 * @returns {HTMLElement} - Élément HTML de la carte
 */
function createReviewCard(review) {
    const card = document.createElement('div');
    card.className = 'review-card';

    // Créer les étoiles en fonction du rating
    const stars = '⭐'.repeat(review.rating || 0);

    card.innerHTML = `
        <div class="review-header">
            <strong>${review.user_name || 'Anonymous'}</strong>
            <span class="review-rating">${stars}</span>
        </div>
        <p class="review-comment">${review.comment || review.text || 'No comment provided.'}</p>
    `;

    return card;
}

// ========================================
// GESTION DE LA PAGE ADD REVIEW
// ========================================

function initAddReviewPage() {
    // Vérifier l'authentification
    if (!isAuthenticated()) {
        window.location.href = 'index.html';
        return;
    }

    // Récupérer l'ID du lieu depuis l'URL
    const urlParams = new URLSearchParams(window.location.search);
    const placeId = urlParams.get('place_id');

    if (!placeId) {
        window.location.href = 'index.html';
        return;
    }

    // Charger les infos du lieu
    loadPlaceInfoForReview(placeId);

    // Gérer le formulaire d'ajout d'avis
    const reviewForm = document.getElementById('review-form');
    if (reviewForm) {
        reviewForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            await submitReview(placeId);
        });
    }

    // Mettre à jour le bouton de connexion
    updateLoginButton();
}

/**
 * Charger les informations du lieu pour l'avis
 * @param {string} placeId - ID du lieu
 */
async function loadPlaceInfoForReview(placeId) {
    try {
        const token = getAuthToken();
        const response = await fetch(`${API_BASE_URL}/places/${placeId}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            const place = await response.json();
            const placeNameElement = document.getElementById('place-name-review');
            if (placeNameElement) {
                placeNameElement.textContent = place.title || 'Unknown Place';
            }
        }
    } catch (error) {
        console.error('Error loading place info:', error);
    }
}

/**
 * Soumettre un avis
 * @param {string} placeId - ID du lieu
 */
async function submitReview(placeId) {
    const reviewText = document.getElementById('review').value.trim();
    const rating = document.getElementById('rating').value;
    const successMessage = document.getElementById('success-message');

    // Validation
    if (!reviewText || !rating) {
        showMessage(successMessage, 'Please fill in all fields.', 'error');
        return;
    }

    try {
        const token = getAuthToken();
        const submitButton = document.querySelector('#review-form button[type="submit"]');
        submitButton.textContent = 'Submitting...';
        submitButton.disabled = true;

        const response = await fetch(`${API_BASE_URL}/places/${placeId}/reviews/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                text: reviewText,
                rating: parseInt(rating)
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || 'Failed to submit review');
        }

        showMessage(successMessage, 'Review submitted successfully!', 'success');

        // Rediriger vers la page de détails après 2 secondes
        setTimeout(() => {
            window.location.href = `place.html?id=${placeId}`;
        }, 2000);

    } catch (error) {
        console.error('Error submitting review:', error);
        showMessage(successMessage, `Error: ${error.message}`, 'error');
        
        const submitButton = document.querySelector('#review-form button[type="submit"]');
        submitButton.textContent = 'Submit Review';
        submitButton.disabled = false;
    }
}

// ========================================
// LECTEUR DE MUSIQUE ULTRA-PERSISTANT
// ========================================

function initMusicPlayer() {
  const playPauseBtn = document.getElementById('play-pause-btn');
  const prevBtn = document.getElementById('prev-btn');
  const nextBtn = document.getElementById('next-btn');
  const progressBar = document.getElementById('progress-bar');
  const volumeSlider = document.getElementById('volume-slider');
  const volumeValue = document.getElementById('volume-value');
  const volumeIcon = document.querySelector('.volume-icon');
  const currentTimeEl = document.getElementById('current-time');
  const durationTimeEl = document.getElementById('duration-time');
  const trackNameEl = document.getElementById('track-name');
  
  if (!playPauseBtn || !progressBar || !trackNameEl) {
      console.log('Music player elements not found');
      return;
  }
  
  const playlist = [
      { src: 'music/song1.mp3', name: 'Chanson 1' },
      { src: 'music/song2.mp3', name: 'Chanson 2' },
      { src: 'music/song3.mp3', name: 'Chanson 3' }
  ];
  
  // Créer un contexte audio global partagé
  let audio;
  const storageKey = 'musicPlayerState';
  
  // Initialiser ou récupérer l'audio
  function initAudio() {
      // Créer un nouvel élément audio
      audio = new Audio();
      audio.loop = false;
      
      // Charger l'état depuis localStorage
      const savedState = JSON.parse(localStorage.getItem(storageKey) || '{}');
      const trackIndex = savedState.trackIndex || 0;
      const volume = savedState.volume || 30;
      const time = savedState.time || 0;
      const isPlaying = savedState.isPlaying || false;
      
      // Configurer l'audio
      audio.src = playlist[trackIndex].src;
      audio.volume = volume / 100;
      audio.currentTime = time;
      
      // Si c'était en lecture, reprendre
      if (isPlaying) {
          setTimeout(() => {
              audio.play().catch(e => console.log('Autoplay prevented'));
          }, 100);
      }
      
      return { trackIndex, volume, time, isPlaying };
  }
  
  const state = initAudio();
  let currentTrack = state.trackIndex;
  
  // Sauvegarder l'état
  function saveState() {
      const stateToSave = {
          trackIndex: currentTrack,
          volume: audio.volume * 100,
          time: audio.currentTime,
          isPlaying: !audio.paused
      };
      localStorage.setItem(storageKey, JSON.stringify(stateToSave));
  }
  
  // Sauvegarder régulièrement
  setInterval(saveState, 500);
  
  // Sauvegarder avant de quitter la page
  window.addEventListener('beforeunload', saveState);
  
  // Formater le temps
  function formatTime(seconds) {
      if (isNaN(seconds) || seconds === Infinity) return '0:00';
      const mins = Math.floor(seconds / 60);
      const secs = Math.floor(seconds % 60);
      return `${mins}:${secs < 10 ? '0' : ''}${secs}`;
  }
  
  // Mettre à jour l'icône du volume
  function updateVolumeIcon(volume) {
      if (!volumeIcon) return;
      if (volume == 0) {
          volumeIcon.textContent = '🔇';
      } else if (volume < 50) {
          volumeIcon.textContent = '🔉';
      } else {
          volumeIcon.textContent = '🔊';
      }
  }
  
  // Charger une piste
  function loadTrack(index) {
      currentTrack = index;
      const wasPlaying = !audio.paused;
      
      audio.src = playlist[currentTrack].src;
      trackNameEl.textContent = playlist[currentTrack].name;
      
      audio.addEventListener('loadedmetadata', function onLoaded() {
          if (durationTimeEl) {
              durationTimeEl.textContent = formatTime(audio.duration);
          }
          if (progressBar) {
              progressBar.max = Math.floor(audio.duration);
          }
          audio.removeEventListener('loadedmetadata', onLoaded);
      });
      
      audio.load();
      
      if (wasPlaying) {
          setTimeout(() => audio.play(), 100);
      }
      
      saveState();
  }
  
  // Initialiser l'UI
  trackNameEl.textContent = playlist[currentTrack].name;
  if (volumeSlider) volumeSlider.value = state.volume;
  if (volumeValue) volumeValue.textContent = `${Math.round(state.volume)}%`;
  updateVolumeIcon(state.volume);
  
  if (state.isPlaying) {
      playPauseBtn.textContent = '⏸️';
  } else {
      playPauseBtn.textContent = '🎵';
  }
  
  // Mise à jour de la progression
  audio.addEventListener('timeupdate', () => {
      if (currentTimeEl) {
          currentTimeEl.textContent = formatTime(audio.currentTime);
      }
      if (progressBar) {
          progressBar.value = Math.floor(audio.currentTime);
      }
  });
  
  audio.addEventListener('loadedmetadata', () => {
      if (durationTimeEl) {
          durationTimeEl.textContent = formatTime(audio.duration);
      }
      if (progressBar) {
          progressBar.max = Math.floor(audio.duration);
      }
  });
  
  // Piste suivante automatique
  audio.addEventListener('ended', () => {
      currentTrack = (currentTrack + 1) % playlist.length;
      loadTrack(currentTrack);
      audio.play();
  });
  
  // Bouton Play/Pause
  playPauseBtn.addEventListener('click', () => {
      if (audio.paused) {
          audio.play().catch(err => {
              console.log('Autoplay prevented:', err);
              alert('Cliquez pour démarrer la musique');
          });
          playPauseBtn.textContent = '⏸️';
      } else {
          audio.pause();
          playPauseBtn.textContent = '🎵';
      }
      saveState();
  });
  
  // Boutons Prev/Next
  if (prevBtn) {
      prevBtn.addEventListener('click', () => {
          currentTrack = (currentTrack - 1 + playlist.length) % playlist.length;
          loadTrack(currentTrack);
      });
  }
  
  if (nextBtn) {
      nextBtn.addEventListener('click', () => {
          currentTrack = (currentTrack + 1) % playlist.length;
          loadTrack(currentTrack);
      });
  }
  
  // Barre de progression
  if (progressBar) {
      progressBar.addEventListener('input', () => {
          audio.currentTime = progressBar.value;
          saveState();
      });
  }
  
  // Volume
  if (volumeSlider) {
      volumeSlider.addEventListener('input', (e) => {
          const volume = e.target.value;
          audio.volume = volume / 100;
          if (volumeValue) volumeValue.textContent = `${volume}%`;
          updateVolumeIcon(volume);
          saveState();
      });
  }
  
  // Mute/Unmute
  if (volumeIcon) {
      volumeIcon.addEventListener('click', () => {
          if (audio.volume > 0) {
              audio.volume = 0;
              if (volumeSlider) volumeSlider.value = 0;
              if (volumeValue) volumeValue.textContent = '0%';
              updateVolumeIcon(0);
          } else {
              audio.volume = 0.3;
              if (volumeSlider) volumeSlider.value = 30;
              if (volumeValue) volumeValue.textContent = '30%';
              updateVolumeIcon(30);
          }
          saveState();
      });
  }
}

// ========================================
// INITIALISATION AU CHARGEMENT DE LA PAGE
// ========================================

document.addEventListener('DOMContentLoaded', () => {
  // Initialiser le lecteur de musique
  initMusicPlayer();
  
  // Déterminer quelle page est chargée
  const currentPage = window.location.pathname.split('/').pop();

  switch (currentPage) {
      case 'login.html':
          initLoginPage();
          break;
      case 'index.html':
      case '':
          initIndexPage();
          break;
      case 'place.html':
          initPlaceDetailsPage();
          break;
      case 'add_review.html':
          initAddReviewPage();
          break;
      default:
          console.log('Unknown page');
  }
});