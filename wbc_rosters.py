"""
WBC 2026 rosters — MLB-affiliated players only.
Source: Baseball America (announced 2026-02-05)
Name format: "Last, First" to match bat_tracking() data.
"""

WBC_ROSTERS: dict[str, list[str]] = {
    "🇺🇸 USA": [
        "Bregman, Alex", "Buxton, Byron", "Carroll, Corbin", "Cleavinger, Garrett",
        "Clement, Ernie", "Crow-Armstrong, Pete", "Goldschmidt, Paul", "Harper, Bryce",
        "Henderson, Gunnar", "Holmes, Clay", "Jax, Griffin", "Judge, Aaron",
        "Keller, Brad", "Kershaw, Clayton", "Boyd, Matt", "McLean, Nolan",
        "Miller, Mason", "Raleigh, Cal", "Ryan, Joe", "Schwarber, Kyle",
        "Skenes, Paul", "Skubal, Tarik", "Smith, Will", "Speier, Gabe",
        "Turang, Brice", "Wacha, Michael", "Webb, Logan", "Whitlock, Garrett",
        "Witt Jr., Bobby", "Bednar, David",
    ],
    "🇯🇵 Japan": [
        "Ohtani, Shohei", "Yamamoto, Yoshinobu", "Kikuchi, Yusei",
        "Suzuki, Seiya", "Yoshida, Masataka", "Matsui, Yusei",
        "Murakami, Munetaka", "Okamoto, Kazuma", "Sugano, Tomoyuki",
    ],
    "🇩🇴 Dominican Rep.": [
        "Alcántara, Sandy", "Alvarado, Elvis", "Brazobán, Huascar", "Bello, Brayan",
        "Caminero, Junior", "Cruz, Oneil", "Domínguez, Seranthony", "Doval, Camilo",
        "Estévez, Carlos", "Guerrero Jr., Vladimir", "Machado, Manny", "Marte, Ketel",
        "Peña, Jeremy", "Peralta, Wandy", "Perdomo, Geraldo", "Ramírez, Agustín",
        "Rodríguez, Julio", "Rojas, Johan", "Rosario, Amed", "Sanchez, Cristopher",
        "Santana, Dennis", "Santana, Carlos", "Severino, Luis", "Soto, Juan",
        "Soto, Gregory", "Tatís Jr., Fernando", "Uribe, Abner", "Uceta, Edwin",
        "Wells, Austin",
    ],
    "🇻🇪 Venezuela": [
        "Acuña Jr., Ronald", "Alvarado, Jose", "Abreu, Wilyer", "Arráez, Luis",
        "Bazardo, Eduard", "Buttó, José", "Chourio, Jackson", "Contreras, Willson",
        "Contreras, William", "De Jesus, Enmanuel", "Garcia, Maikel", "Giménez, Andrés",
        "Gómez, Yoendrys", "Guzman, Carlos", "López, Pablo", "Montero, Keider",
        "Mosqueda, Oddanier", "Palencia, Daniel", "Perez, Salvador",
        "Rodríguez, Eduardo", "Sanoja, Javier", "Senzatela, Antonio",
        "Suárez, Eugenio", "Suárez, Ranger", "Torres, Gleyber", "Tovar, Ezequiel",
        "Zerpa, Angel",
    ],
    "🇵🇷 Puerto Rico": [
        "Arenado, Nolan", "Arroyo, Edwin", "Castro, Willi", "Cortes, Carlos",
        "Cruz, Fernando", "Diaz, Edwin", "Espada, José", "Garcia, Rico",
        "Hernáiz, Darrell", "Lugo, Seth", "Lugo, Matthew", "Morán, Jovani",
        "Quinones, Luis", "Ramos, Heliot", "Ríos, Yacksel", "Rivera, Eduardo",
        "Rodríguez, Elmer", "Torres, Bryan", "Velez, Ricardo", "Vázquez, Luis",
    ],
    "🇲🇽 Mexico": [
        "Aranda, Jonathan", "Arozarena, Randy", "Assad, Javier", "Bernardino, Brennan",
        "Bradley, Taj", "Carrillo, Alex", "Duarte, Daniel", "Duran, Jarren",
        "Garcia, Robert", "Gastelum, Luis", "Gonzales, Nick", "Kirk, Alejandro",
        "Meneses, Joey", "Muñoz, Andrés", "Natera Jr., Samy", "Ortiz, Joey",
        "Osuna, Alejandro", "Serna, Jared", "Thomas, Alek", "Vodnik, Victor",
        "Walker, Taijuan",
    ],
    "🇰🇷 Korea": [
        "Dunning, Dane", "Go, Woo Suk", "Jones, Jahmai", "Kim, Hyeseong",
        "Lee, Jung-Hoo", "O'Brien, Riley", "Whitcomb, Shay",
    ],
    "🇹🇼 Chinese Taipei": [
        "Chen, Po-Yu", "Cheng, Tsung-Che", "Fairchild, Stuart", "Lee, Hao-Yu",
        "Lin, Wei-En", "Lin, Yu-Min", "Long, Jonathon", "Sha, Tzu-Chen",
        "Zhuang, Chen Zhong-Ao",
    ],
    "🇳🇱 Netherlands": [
        "Albies, Ozzie", "Bogaerts, Xander", "Cornelia, Jamdrick", "Croes, Dayson",
        "Estanista, Jaydenn", "Jansen, Kenley", "Jones, Druw", "Kelly, Antwone",
        "Kelly, Jaitoine", "Merite, Ryjeteri", "Oduber, Shawndrick", "Profar, Jurickson",
        "Rafaela, Ceddanne", "Tromp, Chadwick", "Wilson, Dylan",
    ],
    "🇨🇺 Cuba": [
        "Cappe, Yiddi", "Chapman, Emmanuel", "Cruz, Naykel", "Hernandez, Omar",
        "Hurtado, Daviel", "Moncada, Yoán", "Rodriguez, Yariel", "Vargas, Alexander",
    ],
    "🇨🇦 Canada": [
        "Ashman, Micah", "Black, Tyler", "Caissie, Owen", "Cerantola, Eric",
        "Clarke, Denzel", "Diaz, Indigo", "Hicks, Liam", "Jean, Antoine",
        "Julien, Edouard", "Loewen, Carter", "López, Otto", "Macko, Adam",
        "Naylor, Josh", "Naylor, Bo", "O'Neill, Tyler", "Quantrill, Cal",
        "Soroka, Michael", "Taillon, Jameson", "Toro, Abraham", "Wilkinson, Matt",
        "Young, Jared", "Zastryzny, Rob",
    ],
    "🇮🇹 Italy": [
        "Aldegheri, Sam", "Altavilla, Dan", "Antonacci, Sam", "Caglianone, Jac",
        "Canzone, Dominic", "DeLucia, Dylan", "Dezenzo, Zach", "Ercolani, Alessandro",
        "Festa, Matt", "Fischer, Andrew", "Graceffo, Gordon", "Jacob, Alek",
        "La Sorsa, Joe", "Lorenzen, Michael", "Marinaccio, Ron", "Marsee, Jakob",
        "Mastrobuoni, Miles", "Morabito, Nick", "Nicolas, Kyle", "Nola, Aaron",
        "Nori, Dante", "Pasquantino, Vinnie", "Saggese, Thomas", "Teel, Kyle",
        "Weissert, Greg",
    ],
    "🇮🇱 Israel": [
        "Bader, Harrison", "Beilenson, Charlie", "Blum, Josh", "Bowman, Matt",
        "Carrigg, Cole", "Cohen, Harrison", "Geber, Jordan", "Gelof, Jake",
        "Horwitz, Spencer", "Johnston, Troy", "Kremer, Dean", "Lazar, Max",
        "Lequerica, Carlos", "Levenson, Zach", "Mallitz, Josh", "Mendlinger, Noah",
        "Mervis, Matt", "Morgan, Eli", "Prager, Ryan", "Schreck, RJ",
        "Simon, Ben", "Stock, Robert", "Stubbs, Garrett", "Stubbs, CJ",
    ],
    "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Great Britain": [
        "Anderson, Jack", "Beck, Brendan", "Beck, Tristan", "Chisholm Jr., Jazz",
        "Cresswell, Willis", "Eaton, Nate", "Ford, Harry", "Gill Hill, Gary",
        "Johnson, Ivan", "Knowles, Antonio", "Koperniak, Matt", "Langhorne, Miles",
        "Lewis Jr., Ian", "Long, Ryan", "Murray, BJ", "Petersen, Michael",
        "Robinson, Kristian", "Seppings, Jack", "Victor, Najer", "Wild, Owen",
    ],
    "🇵🇦 Panama": [
        "Allen, Logan", "Amaya, Miguel", "Bernal, Leo", "Bethancourt, Christian",
        "Bradfield, Enrique", "Caballero, José", "Cienfuegos, Miguel",
        "González, James", "Guerra, Javy", "Herrera, Ivan", "Jiménez, Leo",
        "Mendoza, Abdiel", "Ramos, Jose", "Rodríguez, Erian", "Sosa, Edmundo",
    ],
    "🇨🇴 Colombia": [
        "Alfaro, Jorge", "Arroyo, Michael", "Bergner, Austin", "Buelvas, Brayan",
        "Campero, Gustavo", "Crismatt, Nabil", "Frias, Dayan", "Guerrero, Tayron",
        "Lorduy, David", "Sanmartín, Reiver", "Zuñiga, Guillo",
    ],
    "🇳🇮 Nicaragua": [
        "Cruz, Stiven", "Hebbert, Duque", "Munguia, Ismael", "Rayo, Oscar",
        "Rodríguez, Carlos", "Vientos, Mark", "Zamora, Freddy",
    ],
    "🇦🇺 Australia": [
        "Bazzana, Travis", "Durrington, Max", "Mead, Curtis",
        "Neunborn, Mitch", "Townsend, Blake",
    ],
    "🇧🇷 Brazil": [
        "Albanez, Pietro", "Barbosa, Gabriel", "Lemos, Pedro",
        "Missaki, Daniel", "Ramirez, Lucas",
    ],
}
