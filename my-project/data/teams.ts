export type League = { id: string; name: string; teams: string[] };

export const LEAGUES: League[] = [
  {
    id: "premier",
    name: "Premier League (Anglia)",
    teams: ["Arsenal", "Aston Villa", "Bournemouth", "Brentford", "Brighton", "Burnley", "Chelsea", "Crystal Palace", "Everton", "Fulham", "Leeds", "Liverpool", "Man City", "Man United", "Newcastle", "Nott'm Forest", "Sunderland", "Tottenham", "West Ham", "Wolves"]
  },
  {
    id: "championship",
    name: "Championship (Anglia)",
    teams: ["Birmingham", "Blackburn", "Bristol City", "Charlton", "Coventry", "Derby", "Hull", "Ipswich", "Leicester", "Middlesbrough", "Millwall", "Norwich", "Oxford", "Portsmouth", "Preston", "QPR", "Sheffield United", "Sheffield Weds", "Southampton", "Stoke", "Swansea", "Watford", "West Brom", "Wrexham"]
  },
  {
    id: "laliga",
    name: "La Liga (Hiszpania)",
    teams: ["Alaves", "Ath Bilbao", "Ath Madrid", "Barcelona", "Betis", "Celta", "Elche", "Espanol", "Getafe", "Girona", "Levante", "Mallorca", "Osasuna", "Oviedo", "Real Madrid", "Sevilla", "Sociedad", "Valencia", "Vallecano", "Villarreal"]
  },
  {
    id: "seriea",
    name: "Serie A (Włochy)",
    teams: ["Atalanta", "Bologna", "Cagliari", "Como", "Cremonese", "Fiorentina", "Genoa", "Inter", "Juventus", "Lazio", "Lecce", "Milan", "Napoli", "Parma", "Pisa", "Roma", "Sassuolo", "Torino", "Udinese", "Verona"]      
  },
  {
    id: "bundesliga",
    name: "Bundesliga (Niemcy)",
    teams: ["Augsburg", "Bayern Munich", "Dortmund", "Ein Frankfurt", "FC Koln", "Freiburg", "Hamburg", "Heidenheim", "Hoffenheim", "Leverkusen", "M'gladbach", "Mainz", "RB Leipzig", "St Pauli", "Stuttgart", "Union Berlin", "Werder Bremen", "Wolfsburg"]
  },
  {
    id: "ligue1",
    name: "Ligue 1 (Francja)",
    teams: ["Angers", "Auxerre", "Brest", "Le Havre", "Lens", "Lille", "Lorient", "Lyon", "Marseille", "Metz", "Monaco", "Nantes", "Nice", "Paris FC", "Paris SG", "Rennes", "Strasbourg", "Toulouse"]
  },
  {
    id: "eredivisie",
    name: "Eredivisie (Holandia)",
    teams: ["AZ Alkmaar", "Ajax", "Excelsior", "Feyenoord", "For Sittard", "Go Ahead Eagles", "Groningen", "Heerenveen", "Heracles", "NAC Breda", "Nijmegen", "PSV Eindhoven", "Sparta Rotterdam", "Telstar", "Twente", "Utrecht", "Volendam", "Zwolle"]
  },
  {
    id: "primeira",
    name: "Primeira Liga (Portugalia)",
    teams: ["AVS", "Alverca", "Arouca", "Benfica", "Casa Pia", "Estoril", "Estrela", "Famalicao", "Gil Vicente", "Guimaraes", "Moreirense", "Nacional", "Porto", "Rio Ave", "Santa Clara", "Sp Braga", "Sp Lisbon", "Tondela"]
  },
  {
    id: "superlig",
    name: "Super Lig (Turcja)",
    teams: ["Alanyaspor", "Antalyaspor", "Besiktas", "Buyuksehyr", "Eyupspor", "Fenerbahce", "Galatasaray", "Gaziantep", "Genclerbirligi", "Goztep", "Karagumruk", "Kasimpasa", "Kayserispor", "Kocaelispor", "Konyaspor", "Rizespor", "Samsunspor", "Trabzonspor"]
  },
  {
    id: "ekstraklasa",
    name: "Ekstraklasa (Polska)",
    teams: ["Arka Gdynia", "Cracovia", "GKS Katowice", "Górnik Zabrze", "Jagiellonia Białystok", "Korona Kielce", "Lech Poznań", "Legia Warszawa", "Piast Gliwice", "Pogoń Szczecin", "Radomiak Radom", "Raków Częstochowa", "Ruch Chorzów", "Stal Mielec", "Widzew Łódź", "Zagłębie Lubin", "ŁKS Łódź", "Śląsk Wrocław"]
  },
];