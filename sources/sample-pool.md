# Sample Pool

> Role: Source pool for SAMPLE mode randomization. Entries are categorized
> by outlet type and tagged on four axes to enable coverage tracking.
> The pool is designed to include a mix of sources likely to exhibit power
> dynamics and sources where power dynamics may be absent (null-case-likely),
> ensuring the framework's calibration sample space produces genuine null cases.
>
> Maintenance: Add entries when the pool's axis coverage has gaps. Remove
> entries only if an outlet ceases to exist. Do not curate for "relevance"
> — the point is randomness.
>
> Generated from data/sample-pool.yaml — do not edit directly.

---

## Axis definitions

- **INST** (institutional type): corporate, independent, wire, government, trade, local, nonprofit, academic
- **DOMAIN** (subject domain): politics, economics, technology, culture, science, local-gov, sports, lifestyle, health, environment, military, legal
- **GEO** (geographic focus): us-national, us-local, uk, eu, global-south, asia, middle-east, africa, non-anglophone
- **AUD** (audience): general, professional, investor, policymaker, academic
- **POS** (framework position): 1–5 per positional-lens.md

---

## Entries

### Corporate media — US national

- **Associated Press** (apnews.com) — [INST:wire] [DOMAIN:politics,economics] [GEO:us-national] [AUD:general] [POS:4]
- **Reuters US** (reuters.com) — [INST:wire] [DOMAIN:politics,economics] [GEO:us-national] [AUD:general,investor] [POS:4]
- **New York Times** (nytimes.com) — [INST:corporate] [DOMAIN:politics,culture] [GEO:us-national] [AUD:general] [POS:5]
- **Washington Post** (washingtonpost.com) — [INST:corporate] [DOMAIN:politics,legal] [GEO:us-national] [AUD:general] [POS:5]
- **Wall Street Journal** (wsj.com) — [INST:corporate] [DOMAIN:economics,politics] [GEO:us-national] [AUD:investor,professional] [POS:5]
- **NPR** (npr.org) — [INST:nonprofit] [DOMAIN:politics,culture] [GEO:us-national] [AUD:general] [POS:5]
- **USA Today** (usatoday.com) — [INST:corporate] [DOMAIN:politics,lifestyle] [GEO:us-national] [AUD:general] [POS:4]
- **CBS News** (cbsnews.com) — [INST:corporate] [DOMAIN:politics,economics] [GEO:us-national] [AUD:general] [POS:4]

### Corporate media — international

- **BBC News** (bbc.com/news) — [INST:corporate] [DOMAIN:politics,economics] [GEO:uk] [AUD:general] [POS:4]
- **The Guardian** (theguardian.com) — [INST:corporate] [DOMAIN:politics,culture] [GEO:uk] [AUD:general] [POS:5]
- **Financial Times** (ft.com) — [INST:corporate] [DOMAIN:economics,politics] [GEO:eu] [AUD:investor,professional] [POS:5]
- **The Economist** (economist.com) — [INST:corporate] [DOMAIN:economics,politics] [GEO:eu] [AUD:professional] [POS:5]
- **Al Jazeera English** (aljazeera.com) — [INST:corporate] [DOMAIN:politics,military] [GEO:middle-east] [AUD:general] [POS:4]
- **South China Morning Post** (scmp.com) — [INST:corporate] [DOMAIN:politics,economics] [GEO:asia] [AUD:general] [POS:4]
- **Sydney Morning Herald** (smh.com.au) — [INST:corporate] [DOMAIN:politics,economics] [GEO:asia] [AUD:general] [POS:4]
- **France 24 English** (france24.com/en) — [INST:corporate] [DOMAIN:politics,culture] [GEO:eu,non-anglophone] [AUD:general] [POS:4]

### Independent / investigative

- **ProPublica** (propublica.org) — [INST:independent] [DOMAIN:politics,legal] [GEO:us-national] [AUD:general] [POS:5]
- **The Intercept** (theintercept.com) — [INST:independent] [DOMAIN:politics,military] [GEO:us-national] [AUD:general] [POS:5]
- **Bellingcat** (bellingcat.com) — [INST:independent] [DOMAIN:military,politics] [GEO:eu] [AUD:general,professional] [POS:5]
- **The Bureau of Investigative Journalism** (thebureauinvestigates.com) — [INST:independent] [DOMAIN:politics,economics] [GEO:uk] [AUD:general] [POS:5]
- **Rest of World** (restofworld.org) — [INST:independent] [DOMAIN:technology,economics] [GEO:global-south] [AUD:general] [POS:5]
- **Organized Crime and Corruption Reporting Project** (occrp.org) — [INST:independent] [DOMAIN:economics,legal] [GEO:eu] [AUD:general,professional] [POS:5]

### Wire services

- **Agence France-Presse** (france24.com/en/afp) — [INST:wire] [DOMAIN:politics,economics] [GEO:eu,non-anglophone] [AUD:general] [POS:4]
- **Xinhua English** (english.news.cn) — [INST:wire] [DOMAIN:politics,economics] [GEO:asia] [AUD:general] [POS:1]
- **TASS English** (tass.com) — [INST:wire] [DOMAIN:politics,military] [GEO:non-anglophone] [AUD:general] [POS:1]

### Government / institutional

- **Congressional Research Service** (crsreports.congress.gov) — [INST:government] [DOMAIN:politics,legal] [GEO:us-national] [AUD:policymaker] [POS:4]
- **Government Accountability Office** (gao.gov) — [INST:government] [DOMAIN:economics,legal] [GEO:us-national] [AUD:policymaker] [POS:4]
- **Federal Register** (federalregister.gov) — [INST:government] [DOMAIN:legal,politics] [GEO:us-national] [AUD:policymaker,professional] [POS:1]
- **European Parliament News** (europarl.europa.eu/news) — [INST:government] [DOMAIN:politics,legal] [GEO:eu] [AUD:policymaker] [POS:4]
- **World Health Organization** (who.int/news) — [INST:government] [DOMAIN:health,politics] [GEO:global-south] [AUD:policymaker,professional] [POS:4]
- **United Nations News** (news.un.org) — [INST:government] [DOMAIN:politics,environment] [GEO:global-south] [AUD:policymaker] [POS:4]

### Trade / professional press

- **Ars Technica** (arstechnica.com) — [INST:trade] [DOMAIN:technology] [GEO:us-national] [AUD:professional] [POS:5]
- **TechCrunch** (techcrunch.com) — [INST:trade] [DOMAIN:technology,economics] [GEO:us-national] [AUD:professional,investor] [POS:4]
- **Defense One** (defenseone.com) — [INST:trade] [DOMAIN:military,politics] [GEO:us-national] [AUD:professional,policymaker] [POS:4]
- **Law360** (law360.com) — [INST:trade] [DOMAIN:legal] [GEO:us-national] [AUD:professional] [POS:4]
- **STAT News** (statnews.com) — [INST:trade] [DOMAIN:health,science] [GEO:us-national] [AUD:professional] [POS:5]
- **The Trade** (thetradenews.com) — [INST:trade] [DOMAIN:economics] [GEO:uk] [AUD:investor,professional] [POS:4]
- **Hacker News** (news.ycombinator.com) — [INST:trade] [DOMAIN:technology] [GEO:us-national] [AUD:professional] [POS:5]
- **Politico** (politico.com) — [INST:trade] [DOMAIN:politics] [GEO:us-national] [AUD:policymaker,professional] [POS:4]

### Local news

- **Chicago Tribune** (chicagotribune.com) — [INST:local] [DOMAIN:local-gov,politics] [GEO:us-local] [AUD:general] [POS:4]
- **Houston Chronicle** (houstonchronicle.com) — [INST:local] [DOMAIN:local-gov,economics] [GEO:us-local] [AUD:general] [POS:4]
- **Minneapolis Star Tribune** (startribune.com) — [INST:local] [DOMAIN:local-gov,politics] [GEO:us-local] [AUD:general] [POS:4]
- **The Arizona Republic** (azcentral.com) — [INST:local] [DOMAIN:local-gov,politics] [GEO:us-local] [AUD:general] [POS:4]
- **The Seattle Times** (seattletimes.com) — [INST:local] [DOMAIN:local-gov,technology] [GEO:us-local] [AUD:general] [POS:4]
- **Manchester Evening News** (manchestereveningnews.co.uk) — [INST:local] [DOMAIN:local-gov,culture] [GEO:uk] [AUD:general] [POS:4]

### Null-case-likely: Sports

- **ESPN** (espn.com) — [INST:corporate] [DOMAIN:sports] [GEO:us-national] [AUD:general] [POS:4]
- **The Athletic** (theathletic.com) — [INST:corporate] [DOMAIN:sports] [GEO:us-national] [AUD:general] [POS:5]
- **BBC Sport** (bbc.com/sport) — [INST:corporate] [DOMAIN:sports] [GEO:uk] [AUD:general] [POS:4]
- **Cricinfo** (espncricinfo.com) — [INST:corporate] [DOMAIN:sports] [GEO:asia] [AUD:general] [POS:4]

### Null-case-likely: Lifestyle / food

- **Bon Appetit** (bonappetit.com) — [INST:corporate] [DOMAIN:lifestyle] [GEO:us-national] [AUD:general] [POS:4]
- **Serious Eats** (seriouseats.com) — [INST:independent] [DOMAIN:lifestyle] [GEO:us-national] [AUD:general] [POS:5]
- **Lonely Planet** (lonelyplanet.com) — [INST:corporate] [DOMAIN:lifestyle] [GEO:eu] [AUD:general] [POS:4]
- **Apartment Therapy** (apartmenttherapy.com) — [INST:independent] [DOMAIN:lifestyle] [GEO:us-national] [AUD:general] [POS:4]
- **Allrecipes** (allrecipes.com) — [INST:corporate] [DOMAIN:lifestyle] [GEO:us-national] [AUD:general] [POS:4]

### Null-case-likely: Science / nature

- **Quanta Magazine** (quantamagazine.org) — [INST:nonprofit] [DOMAIN:science] [GEO:us-national] [AUD:general,academic] [POS:5]
- **Nature News** (nature.com/news) — [INST:academic] [DOMAIN:science] [GEO:uk] [AUD:academic,professional] [POS:5]
- **Phys.org** (phys.org) — [INST:independent] [DOMAIN:science,technology] [GEO:us-national] [AUD:general] [POS:5]

### Academic / research

- **Brookings Institution** (brookings.edu) — [INST:academic] [DOMAIN:politics,economics] [GEO:us-national] [AUD:policymaker,academic] [POS:5]
- **RAND Corporation** (rand.org) — [INST:academic] [DOMAIN:military,politics] [GEO:us-national] [AUD:policymaker,academic] [POS:5]
- **Council on Foreign Relations** (cfr.org) — [INST:academic] [DOMAIN:politics,military] [GEO:us-national] [AUD:policymaker,academic] [POS:5]

### Non-anglophone (English editions)

- **Deutsche Welle** (dw.com/en) — [INST:corporate] [DOMAIN:politics,culture] [GEO:eu,non-anglophone] [AUD:general] [POS:4]
- **NHK World** (www3.nhk.or.jp/nhkworld) — [INST:corporate] [DOMAIN:politics,culture] [GEO:asia,non-anglophone] [AUD:general] [POS:4]
- **The Times of India** (timesofindia.indiatimes.com) — [INST:corporate] [DOMAIN:politics,economics] [GEO:asia] [AUD:general] [POS:4]
- **Daily Maverick** (dailymaverick.co.za) — [INST:independent] [DOMAIN:politics,economics] [GEO:africa] [AUD:general] [POS:5]
- **Rappler** (rappler.com) — [INST:independent] [DOMAIN:politics,technology] [GEO:asia] [AUD:general] [POS:5]
- **Haaretz English** (haaretz.com) — [INST:corporate] [DOMAIN:politics,military] [GEO:middle-east] [AUD:general] [POS:5]
