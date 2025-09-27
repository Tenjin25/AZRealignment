// Loading indicator management
class LoadingManager {
    constructor() {
        this.createElements();
        this.progress = 0;
        this.loadingTasks = 0;
    }

    createElements() {
        // Create loading overlay
        this.overlay = document.createElement('div');
        this.overlay.className = 'loading-overlay';
        this.overlay.style.display = 'none';
        
        this.spinner = document.createElement('div');
        this.spinner.className = 'spinner';
        this.overlay.appendChild(this.spinner);

        // Create progress bar
        this.progressBar = document.createElement('div');
        this.progressBar.className = 'progress-bar';
        
        this.progressFill = document.createElement('div');
        this.progressFill.className = 'fill';
        this.progressBar.appendChild(this.progressFill);

        // Add to document
        document.body.appendChild(this.overlay);
        document.body.appendChild(this.progressBar);
    }

    show() {
        this.overlay.style.display = 'flex';
    }

    hide() {
        this.overlay.style.display = 'none';
        this.setProgress(0);
    }

    setProgress(percent) {
        this.progressFill.style.width = `${percent}%`;
    }

    startTask() {
        this.loadingTasks++;
        this.show();
    }

    completeTask() {
        this.loadingTasks--;
        this.progress = ((this.loadingTasks > 0 ? 1 : 0) / this.loadingTasks) * 100;
        this.setProgress(this.progress);
        
        if (this.loadingTasks === 0) {
            this.hide();
        }
    }
}

// Analytics management
class AnalyticsManager {
    constructor() {
        this.consentKey = 'analytics_consent';
        this.createConsentBanner();
        this.checkConsent();
    }

    createConsentBanner() {
        this.banner = document.createElement('div');
        this.banner.className = 'analytics-consent';
        this.banner.style.display = 'none';
        
        this.banner.innerHTML = `
            <span>We use analytics cookies to understand how you use our website. 
                  This helps us improve our services.</span>
            <div>
                <button class="accept">Accept</button>
                <button class="decline">Decline</button>
            </div>
        `;

        document.body.appendChild(this.banner);

        this.banner.querySelector('.accept').addEventListener('click', () => this.setConsent(true));
        this.banner.querySelector('.decline').addEventListener('click', () => this.setConsent(false));
    }

    checkConsent() {
        const consent = localStorage.getItem(this.consentKey);
        if (consent === null) {
            this.banner.style.display = 'flex';
        } else if (consent === 'true') {
            this.initializeAnalytics();
        }
    }

    setConsent(accepted) {
        localStorage.setItem(this.consentKey, accepted);
        this.banner.style.display = 'none';
        
        if (accepted) {
            this.initializeAnalytics();
        }
    }

    initializeAnalytics() {
        // Initialize Google Analytics
        if (typeof gtag === 'undefined') {
            const script = document.createElement('script');
            script.async = true;
            script.src = 'https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX'; // Replace with your GA ID
            document.head.appendChild(script);

            window.dataLayer = window.dataLayer || [];
            window.gtag = function() { dataLayer.push(arguments); }
            gtag('js', new Date());
            gtag('config', 'G-XXXXXXXXXX'); // Replace with your GA ID
        }
    }

    trackEvent(category, action, label) {
        if (typeof gtag !== 'undefined') {
            gtag('event', action, {
                'event_category': category,
                'event_label': label
            });
        }
    }
}

// Social sharing management
class SocialShare {
    static createButtons(container, url, title) {
        const encodedUrl = encodeURIComponent(url || window.location.href);
        const encodedTitle = encodeURIComponent(title || document.title);

        const buttons = [
            {
                platform: 'twitter',
                url: `https://twitter.com/intent/tweet?url=${encodedUrl}&text=${encodedTitle}`,
                label: 'Share on Twitter'
            },
            {
                platform: 'linkedin',
                url: `https://www.linkedin.com/sharing/share-offsite/?url=${encodedUrl}`,
                label: 'Share on LinkedIn'
            },
            {
                platform: 'reddit',
                url: `https://reddit.com/submit?url=${encodedUrl}&title=${encodedTitle}`,
                label: 'Share on Reddit'
            }
        ];

        buttons.forEach(btn => {
            const link = document.createElement('a');
            link.href = btn.url;
            link.className = `share-button ${btn.platform}`;
            link.textContent = btn.label;
            link.target = '_blank';
            link.rel = 'noopener noreferrer';
            
            container.appendChild(link);
        });
    }
}

// Mobile device warning
class MobileWarning {
    static show() {
        if (window.innerWidth <= 768) {
            const warning = document.createElement('div');
            warning.className = 'mobile-warning';
            warning.textContent = 'This visualization works best on a larger screen. For the best experience, please view on a tablet or desktop device.';
            document.body.appendChild(warning);
        }
    }
}

// Export managers for use in other files
window.LoadingManager = LoadingManager;
window.AnalyticsManager = AnalyticsManager;
window.SocialShare = SocialShare;
window.MobileWarning = MobileWarning;
