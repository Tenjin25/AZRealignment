// Initialize map
mapboxgl.accessToken = 'pk.eyJ1IjoiVGVuamluMjUiLCJhIjoiY21kcW8yeDB2MDhvbTJzb29qeGp1aDZmZCJ9.Zw_i6U-dL7_bEKRHTUh7yg';

const map = new mapboxgl.Map({
    container: 'map',
    style: 'mapbox://styles/mapbox/light-v11',
    center: [-79.0, 35.5],
    zoom: 6.5
});

let electionData = null;
let currentMode = 'county';
let countiesLoaded = false;
let precinctsLoaded = false;
let currentElectionResults = null;
let swingArrows = [];

// County name mapping for election data
const countyNameMap = {
    'ALAMANCE': 'Alamance', 'ALEXANDER': 'Alexander', 'ALLEGHANY': 'Alleghany',
    'ANSON': 'Anson', 'ASHE': 'Ashe', 'AVERY': 'Avery', 'BEAUFORT': 'Beaufort',
    'BERTIE': 'Bertie', 'BLADEN': 'Bladen', 'BRUNSWICK': 'Brunswick',
    'BUNCOMBE': 'Buncombe', 'BURKE': 'Burke', 'CABARRUS': 'Cabarrus',
    'CALDWELL': 'Caldwell', 'CAMDEN': 'Camden', 'CARTERET': 'Carteret',
    'CASWELL': 'Caswell', 'CATAWBA': 'Catawba', 'CHATHAM': 'Chatham',
    'CHEROKEE': 'Cherokee', 'CHOWAN': 'Chowan', 'CLAY': 'Clay',
    'CLEVELAND': 'Cleveland', 'COLUMBUS': 'Columbus', 'CRAVEN': 'Craven',
    'CUMBERLAND': 'Cumberland', 'CURRITUCK': 'Currituck', 'DARE': 'Dare',
    'DAVIDSON': 'Davidson', 'DAVIE': 'Davie', 'DUPLIN': 'Duplin',
    'DURHAM': 'Durham', 'EDGECOMBE': 'Edgecombe', 'FORSYTH': 'Forsyth',
    'FRANKLIN': 'Franklin', 'GASTON': 'Gaston', 'GATES': 'Gates',
    'GRAHAM': 'Graham', 'GRANVILLE': 'Granville', 'GREENE': 'Greene',
    'GUILFORD': 'Guilford', 'HALIFAX': 'Halifax', 'HARNETT': 'Harnett',
    'HAYWOOD': 'Haywood', 'HENDERSON': 'Henderson', 'HERTFORD': 'Hertford',
    'HOKE': 'Hoke', 'HYDE': 'Hyde', 'IREDELL': 'Iredell', 'JACKSON': 'Jackson',
    'JOHNSTON': 'Johnston', 'JONES': 'Jones', 'LEE': 'Lee', 'LENOIR': 'Lenoir',
    'LINCOLN': 'Lincoln', 'MCDOWELL': 'McDowell', 'MACON': 'Macon',
    'MADISON': 'Madison', 'MARTIN': 'Martin', 'MECKLENBURG': 'Mecklenburg',
    'MITCHELL': 'Mitchell', 'MONTGOMERY': 'Montgomery', 'MOORE': 'Moore',
    'NASH': 'Nash', 'NEW HANOVER': 'New Hanover', 'NORTHAMPTON': 'Northampton',
    'ONSLOW': 'Onslow', 'ORANGE': 'Orange', 'PAMLICO': 'Pamlico',
    'PASQUOTANK': 'Pasquotank', 'PENDER': 'Pender', 'PERQUIMANS': 'Perquimans',
    'PERSON': 'Person', 'PITT': 'Pitt', 'POLK': 'Polk', 'RANDOLPH': 'Randolph',
    'RICHMOND': 'Richmond', 'ROBESON': 'Robeson', 'ROCKINGHAM': 'Rockingham',
    'ROWAN': 'Rowan', 'RUTHERFORD': 'Rutherford', 'SAMPSON': 'Sampson',
    'SCOTLAND': 'Scotland', 'STANLY': 'Stanly', 'STOKES': 'Stokes',
    'SURRY': 'Surry', 'SWAIN': 'Swain', 'TRANSYLVANIA': 'Transylvania',
    'TYRRELL': 'Tyrrell', 'UNION': 'Union', 'VANCE': 'Vance', 'WAKE': 'Wake',
    'WARREN': 'Warren', 'WASHINGTON': 'Washington', 'WATAUGA': 'Watauga',
    'WAYNE': 'Wayne', 'WILKES': 'Wilkes', 'WILSON': 'Wilson',
    'YADKIN': 'Yadkin', 'YANCEY': 'Yancey'
};

function updateStatus(message) {
    document.getElementById('status').innerHTML = `<strong>Status:</strong> ${message}`;
    console.log(message);
}

// Toggle main controls minimize/expand
function toggleMainControls() {
    const controls = document.getElementById('main-controls');
    const btn = document.getElementById('controls-minimize-btn');
    
    if (controls.classList.contains('minimized')) {
        controls.classList.remove('minimized');
        btn.textContent = '−';
    } else {
        controls.classList.add('minimized');
        btn.textContent = '+';
    }
}

// Toggle sidebar minimize/expand
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const btn = document.getElementById('sidebar-minimize-btn');
    const floatingBtn = document.getElementById('floating-expand-btn');
    const mapElement = document.getElementById('map');
    const body = document.body;
    
    if (sidebar.classList.contains('minimized')) {
        sidebar.classList.remove('minimized');
        mapElement.classList.remove('sidebar-minimized');
        body.classList.remove('sidebar-minimized');
        btn.textContent = '−';
        floatingBtn.style.display = 'none';
        setTimeout(() => map.resize(), 300);
    } else {
        sidebar.classList.add('minimized');
        mapElement.classList.add('sidebar-minimized');
        body.classList.add('sidebar-minimized');
        btn.textContent = '+';
        floatingBtn.style.display = 'flex';
        setTimeout(() => map.resize(), 300);
    }
}

// Toggle legend minimize/expand
function toggleLegend() {
    const legend = document.getElementById('legend');
    const btn = document.getElementById('legend-minimize-btn');
    
    if (legend.classList.contains('minimized')) {
        legend.classList.remove('minimized');
        btn.textContent = '−';
    } else {
        legend.classList.add('minimized');
        btn.textContent = '+';
    }
}

// Calculate and display statewide results
function updateStatewideResults(results, contest, year) {
    let demTotal = 0, repTotal = 0, totalVotes = 0;
    
    Object.values(results).forEach(result => {
        if (result.dem_votes && result.rep_votes) {
            demTotal += result.dem_votes;
            repTotal += result.rep_votes;
            totalVotes += result.dem_votes + result.rep_votes;
        }
    });
    
    if (totalVotes === 0) {
        document.getElementById('statewide-content').innerHTML = 
            '<p>No statewide data available for this contest.</p>';
        return;
    }
    
    const demPercent = (demTotal / totalVotes * 100);
    const repPercent = (repTotal / totalVotes * 100);
    const margin = Math.abs(demPercent - repPercent);
    const winner = demPercent > repPercent ? 'Democratic' : 'Republican';
    const winnerPercent = Math.max(demPercent, repPercent);
    const loserPercent = Math.min(demPercent, repPercent);
    
    let category;
    if (margin >= 40) {
        category = `Annihilation ${winner}`;
    } else if (margin >= 30) {
        category = `Dominant ${winner}`;
    } else if (margin >= 20) {
        category = `Stronghold ${winner}`;
    } else if (margin >= 10) {
        category = `Safe ${winner}`;
    } else if (margin >= 5.5) {
        category = `Likely ${winner}`;
    } else if (margin >= 1) {
        category = `Lean ${winner}`;
    } else if (margin >= 0.5) {
        category = `Tilt ${winner}`;
    } else {
        category = 'Tossup';
    }
    
    const marginText = `${winner} +${margin.toFixed(1)}%`;
    
    document.getElementById('statewide-content').innerHTML = `
        <div class="statewide-margin">
            <div class="margin-text" style="color: ${winner === 'Democratic' ? '#1e40af' : '#dc2626'}">${marginText}</div>
            <div class="margin-details">
                ${winnerPercent.toFixed(1)}% vs ${loserPercent.toFixed(1)}% • ${category}
            </div>
            <div class="margin-details">
                ${demTotal.toLocaleString()} D, ${repTotal.toLocaleString()} R • ${totalVotes.toLocaleString()} total votes
            </div>
        </div>
    `;
}

function setMode(mode) {
    console.log(`Setting mode to: ${mode}`);
    currentMode = mode;
    document.getElementById('county-mode').classList.toggle('active', mode === 'county');
    document.getElementById('precinct-mode').classList.toggle('active', mode === 'precinct');
    
    if (mode === 'county') {
        updateStatus(`Switched to County Results mode - shows actual county winners`);
    } else {
        updateStatus(`Switched to Precinct Patterns mode - shows dominant precinct categories`);
    }
    
    if (currentElectionResults) {
        console.log('Reapplying categories after mode change');
        const contest = document.getElementById('contest').value;
        console.log(`Current contest: ${contest}`);
        applyCategories();
    } else {
        console.log('No election results loaded yet');
    }
}

function applyCategories() {
    if (!electionData || !countiesLoaded) {
        updateStatus('❌ Data not ready yet!');
        return;
    }
    
    const contestElement = document.getElementById('contest');
    
    if (!contestElement) {
        updateStatus('❌ Contest dropdown not found!');
        return;
    }
    
    const contest = contestElement.value;
    
    if (!contest) {
        updateStatus('❌ Please select a contest!');
        return;
    }
    
    const yearMatch = contest.match(/_(\d{4})_/);
    if (!yearMatch) {
        updateStatus('❌ Could not determine year from contest selection!');
        return;
    }
    const year = yearMatch[1];
    
    updateStatus(`🔍 Loading ${year} precinct and county data...`);
    
    const contestParts = contest.split('_');
    let contestType = contestParts[0];

    // Map contestType to backend key
    if (contestType === 'us') {
        contestType = 'us_senate';
    } else if (contestType === 'attorney') {
        contestType = 'attorney_general';
    } else if (contestType === 'lt') {
        contestType = 'lt_governor';
    } else if (contestType === 'commissioner') {
        contestType = contestParts[0] + '_' + contestParts[1];
    } else if (contestType === 'state') {
        contestType = 'state_auditor';
    } else if (contestType === 'secretary') {
        contestType = 'secretary_of_state';
    } else if (contestType === 'treasurer') {
        contestType = 'treasurer';
    } else if (contestType === 'auditor') {
        contestType = 'state_auditor';
    } else if (contestType === 'superintendent') {
        contestType = 'superintendent_instruction';
    }

    console.log('Contest type:', contestType, 'from value:', contest);
    updateStatus(`🔍 Loading ${contestType} ${year}...`);
    
    console.log('Available years:', Object.keys(electionData.results_by_year || {}));
    if (electionData.results_by_year[year]) {
        console.log(`Available contests for ${year}:`, Object.keys(electionData.results_by_year[year]));
    }
    
    if (!electionData.results_by_year[year]) {
        updateStatus(`❌ No data for year ${year}`);
        return;
    }
    
    if (!electionData.results_by_year[year][contestType]) {
        updateStatus(`❌ No ${contestType} data for ${year}`);
        return;
    }
    
    const contestGroup = electionData.results_by_year[year][contestType];
    const contestKey = Object.keys(contestGroup)[0];
    const contestData = contestGroup[contestKey];
    
    if (!contestData.results) {
        updateStatus(`❌ No results found for ${contestKey}`);
        return;
    }
    
    const results = contestData.results;
    currentElectionResults = results;
    const precinctCount = Object.keys(results).length;
    updateStatus(`📊 Processing ${precinctCount} precincts for ${contestType} ${year}...`);
    
    updateStatewideResults(results, contestType, year);
    console.log(`Found ${precinctCount} precincts for ${contestType} ${year}`);
    
    if (currentMode === 'county') {
        applyCountyCategories(results, contestType, year);
    } else {
        applyPrecinctCategories(results, contestType, year);
    }
}

// Continue with the rest of the functions in the next part...
