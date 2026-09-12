/* ================= GLOBAL STATE =================
   Everything the rest of the app reads/writes lives on `state`.
   Once the backend is wired in (see api.js), the mock `houses` /
   `SOCIETIES` data below gets replaced by responses from
   GET /api/users, /api/listings, /api/grid-status, etc.
*/
const state = {
  authMode:'login',
  inquiry:{ area:'', city:'', pin:'', solar:null, situation:null, goal:null },
  role:'buy', // 'buy' | 'sell' | 'both'
  society:null,
  userHouse:'C4',
  gridRetail:9.50,
  houses:{
    A2:{block:'A', color:'gold', name:'Rahul Sharma', capacity:'5 kW', available:6.0, price:6.20},
    A4:{block:'A', color:'gold', name:'Priya Nair',   capacity:'4 kW', available:4.5, price:6.40},
    B1:{block:'B', color:'gold', name:'Vikram Desai', capacity:'6 kW', available:8.0, price:6.10},
    B4:{block:'B', color:'gold', name:'Anita Joshi',  capacity:'5 kW', available:5.5, price:6.50},
    C2:{block:'C', color:'gold', name:'Kunal Mehta',  capacity:'6 kW', available:7.0, price:6.30},
    D1:{block:'D', color:'gold', name:'Sneha Rao',    capacity:'4 kW', available:3.5, price:6.70},
    D3:{block:'D', color:'red', name:'Chawla'},
    C4:{block:'C', color:'cyan', name:'You (Home)'},
    A1:{block:'A', color:'muted', name:'Mehta'},
    A3:{block:'A', color:'muted', name:'Iyer'},
    B2:{block:'B', color:'muted', name:'Rawat'},
    B3:{block:'B', color:'muted', name:'Saxena'},
    C1:{block:'C', color:'muted', name:'Nair'},
    C3:{block:'C', color:'muted', name:'Bose'},
    D2:{block:'D', color:'muted', name:'Kapoor'},
    D4:{block:'D', color:'muted', name:'Verma'}
  },
  currentHouseId:null,
  selectedHouseId:null,
  need:5.0,
  recommendedId:null,
  buyContext:null,
  sellSurplusTotal:8.0,
  sellQty:6.0,
  sellPrice:6.20,
  tradeCounter:10482,
  trades:[]
};

const BLOCKS = ['A','B','C','D'];
const ROWS = 4;

function blockDistance(a,b){
  if(a===b) return 0;
  const ia=BLOCKS.indexOf(a), ib=BLOCKS.indexOf(b);
  return Math.abs(ia-ib);
}

/* ---- SVG grid geometry (house-grid coordinates) ---- */
const COL_X = [138,248,358,468];      // house centers
const ROW_Y = [117,227,337,447];
const JX = [135,245,355,465];         // grid-wire junction points
const JY = [90,200,310,420];
const CARD_X = [87,197,307,417];      // glass card top-left
const CARD_Y = [42,152,262,372];

/* ---- Mock society list (replace with GET /api/societies or similar) ---- */
const SOCIETIES = [
  {name:'Green Valley Society', dist:'2.4 km away', sellers:12, buyers:4, homes:14, available:'34.5 kWh'},
  {name:'Ashoka Society', dist:'1.8 km away', sellers:8, buyers:3, homes:10, available:'21.0 kWh'},
  {name:'Sunrise Residency', dist:'3.1 km away', sellers:11, buyers:6, homes:13, available:'29.8 kWh'},
  {name:'Shivam Heights', dist:'2.7 km away', sellers:5, buyers:2, homes:7, available:'12.4 kWh'}
];

/* ---- Onboarding-flow / step-bar config ---- */
const FLOWS = {
  buy: ['page-inquiry','page-society','page-map'],
  sell: ['page-inquiry','page-society','page-sell'],
  both: ['page-inquiry','page-society','page-map','page-sell']
};
const STEP_LABELS = {
  'page-inquiry':'Inquiry','page-society':'Select Society','page-map':'Society Map',
  'page-sell':'Sell Surplus'
};
