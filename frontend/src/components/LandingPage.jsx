import React from 'react';

export default function LandingPage({ onLogin }) {
  return (
    <div className="landing-page">
      {/* HERO */}
      <header className="landing-nav">
        <div className="landing-brand">
          <img src="/logo.png" alt="Logo" style={{ width: '28px', height: '28px', borderRadius: '50%', objectFit: 'contain' }} />
          MammoScan AI
        </div>
        <button className="btn-primary" onClick={onLogin}>Se connecter</button>
      </header>

      <section className="landing-hero">
        <div className="hero-content">
          <span className="hero-badge">Powered by DenseNet121 AI</span>
          <h1>La détection précoce <br /><span style={{ color: 'var(--primary-color)' }}>sauve des vies</span></h1>
          <p className="hero-subtitle">
            MammoScan AI assiste les équipes médicales dans l'analyse des mammographies grâce à 
            l'intelligence artificielle, pour une détection plus rapide et plus fiable du cancer du sein.
          </p>
          <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
            <button className="btn-primary btn-lg" onClick={onLogin}>Accéder à la plateforme →</button>
            <a href="#awareness" className="btn-secondary btn-lg">En savoir plus</a>
          </div>
        </div>
        <div className="hero-visual">
          <div className="hero-rings">
            <div className="ring ring1"></div>
            <div className="ring ring2"></div>
            <div className="ring ring3"></div>
            <div className="hero-icon">
              <img src="/logo.png" alt="Icon" style={{ width: '100px', height: '100px', borderRadius: '50%' }} />
            </div>
          </div>
        </div>
      </section>

      {/* STATS */}
      <section className="landing-stats">
        <div className="stat-pill">
          <span className="stat-number">2.3M</span>
          <span className="stat-desc">nouveaux cas / an dans le monde</span>
        </div>
        <div className="stat-pill">
          <span className="stat-number">90%</span>
          <span className="stat-desc">de chances de guérison si détecté tôt</span>
        </div>
        <div className="stat-pill">
          <span className="stat-number">#1</span>
          <span className="stat-desc">cancer le plus fréquent chez la femme</span>
        </div>
      </section>

      {/* AWARENESS */}
      <section className="landing-section" id="awareness">
        <div className="section-inner">
          <h2>Ce que vous devez savoir</h2>
          <p className="section-subtitle">Le cancer du sein est traitable s'il est détecté à un stade précoce.</p>

          <div className="info-cards">
            <div className="info-card">
              <div className="info-icon">🔬</div>
              <h3>Qu'est-ce que le cancer du sein ?</h3>
              <p>
                Le cancer du sein se développe lorsque des cellules mammaires se multiplient de façon 
                incontrôlée. Il peut toucher les deux sexes, bien qu'il soit beaucoup plus fréquent 
                chez les femmes.
              </p>
            </div>
            <div className="info-card">
              <div className="info-icon">⚡</div>
              <h3>Facteurs de risque</h3>
              <p>
                Âge avancé, antécédents familiaux, mutations génétiques (BRCA1/BRCA2), 
                exposition aux hormones, mode de vie sédentaire et consommation d'alcool 
                peuvent augmenter le risque.
              </p>
            </div>
            <div className="info-card">
              <div className="info-icon">🎯</div>
              <h3>Signes à surveiller</h3>
              <p>
                Toute modification de l'aspect ou de la taille du sein, une bosse, 
                des changements au niveau du mamelon, ou des douleurs persistantes doivent 
                être signalés rapidement à un professionnel de santé.
              </p>
            </div>
            <div className="info-card">
              <div className="info-icon">🛡️</div>
              <h3>Prévention & dépistage</h3>
              <p>
                La mammographie régulière (recommandée tous les 2 ans après 50 ans), 
                l'auto-examen mensuel et un mode de vie sain sont les meilleurs outils 
                de prévention disponibles.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* HOW IT WORKS */}
      <section className="landing-section landing-dark">
        <div className="section-inner">
          <h2>Comment fonctionne MammoScan AI ?</h2>
          <p className="section-subtitle">Un workflow médical structuré en 3 étapes</p>

          <div className="steps-row">
            <div className="step-card">
              <div className="step-num">1</div>
              <h3>Upload du scan</h3>
              <p>Le personnel médical uploade la mammographie et renseigne les informations du patient.</p>
            </div>
            <div className="step-arrow">→</div>
            <div className="step-card">
              <div className="step-num">2</div>
              <h3>Analyse IA</h3>
              <p>Notre modèle DenseNet121 analyse l'image et prédit le niveau de risque avec un score de confiance.</p>
            </div>
            <div className="step-arrow">→</div>
            <div className="step-card">
              <div className="step-num">3</div>
              <h3>Validation médicale</h3>
              <p>Le médecin confirme ou corrige le résultat et ajoute ses notes cliniques au dossier patient.</p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="landing-cta">
        <h2>Prêt à accéder à la plateforme ?</h2>
        <p>Connectez-vous pour accéder au portail sécurisé MammoScan AI.</p>
        <button className="btn-primary btn-lg" onClick={onLogin}>Se connecter →</button>
      </section>

      <footer className="landing-footer">
        <p>© 2026 MammoScan AI — Outil d'aide à la décision médicale. Ne remplace pas un diagnostic médical professionnel.</p>
      </footer>
    </div>
  );
}
