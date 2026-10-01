# FICHIER TEMPORAIRE, NON EXÉCUTÉ : blocs de 04_02_streamlit_app.py en attente de migration vers leur page.
# Chaque bloc en est retiré au moment où il est déplacé dans streamlit_pages/.


#========================================================================================
# SECTION TESTS
#========================================================================================
if menu == "🪣 Tests" :
    st.markdown("Mon bac à sable 🪣")
    
    
    st.markdown("#### Corrélation entre comptes récemment activés et risque")
    
    col_graph, col_comment = st.columns([2,1])
    # 1. Définition des cycles chronologiques
    cycles = [
        {'mois': 'Mai (M-5)', 'curr_bill': 'BILL_AMT5', 'dormant_cols': [6]},
        {'mois': 'Juin (M-4)', 'curr_bill': 'BILL_AMT4', 'dormant_cols': [6, 5]},
        {'mois': 'Juillet (M-3)', 'curr_bill': 'BILL_AMT3', 'dormant_cols': [6, 5, 4]},
        {'mois': 'Août (M-2)', 'curr_bill': 'BILL_AMT2', 'dormant_cols': [6, 5, 4, 3]},
        {'mois': 'Septembre (M-1)', 'curr_bill': 'BILL_AMT1', 'dormant_cols': [6, 5, 4, 3, 2]}
    ]

    # Calculs des réactivations et du taux de défaut
    resultats = []

    for c in cycles:
        nom_mois = c['mois']
        curr_bill = c['curr_bill']
        curr_pay = curr_bill.replace('BILL_AMT', 'PAY_AMT')
        dormant_cols = c['dormant_cols']
        
        # Masque de dormance cumulée : BILL_AMT <= 0 ET PAY_AMT == 0 sur TOUS les mois antérieurs
        mask_inactif_cumul = pd.Series(True, index=df.index)
        for m in dormant_cols:
            mask_inactif_cumul &= (df[f'BILL_AMT{m}'] <= 0) & (df[f'PAY_AMT{m}'] == 0)
        
        # Masque de sortie de sommeil au mois courant (facture > 0 OU paiement > 0)
        mask_reactivation = mask_inactif_cumul & ((df[curr_bill] > 0) | (df[curr_pay] > 0))
        nb_reactives = mask_reactivation.sum()
        
        # Calcul du taux de défaut pour cette population
        if nb_reactives > 0:
            nb_defauts = df.loc[mask_reactivation, 'dpnm'].sum()
            tx_defaut = (nb_defauts / nb_reactives) * 100
        else:
            tx_defaut = 0.0
        
        resultats.append({
            'Mois de réactivation': nom_mois,
            'Nombre de réactivations': nb_reactives,
            'Taux de défaut': tx_defaut
        })

    df_res = pd.DataFrame(resultats)

    # 2. Création du graphique Plotly avec double axe Y
    fig_defaut_dormant = make_subplots(specs=[[{"secondary_y": True}]])

    # Axe Y principal : Barres pour le nombre de réactivations
    fig_defaut_dormant.add_trace(
        go.Bar(
            x=df_res['Mois de réactivation'],
            y=df_res['Nombre de réactivations'],
            name="Activations",
            marker_color='#1f77b4',
            text=df_res['Nombre de réactivations'],
            textposition='outside',
            textfont=dict(size=15, color='black'),
            hovertemplate="<b>%{x}</b><br>Comptes réactivés : %{y}<extra></extra>"
        ),
        secondary_y=False
    )

    # Axe Y secondaire : Ligne + marqueurs pour le taux de défaut
    fig_defaut_dormant.add_trace(
        go.Scatter(
            x=df_res['Mois de réactivation'],
            y=df_res['Taux de défaut'],
            name="Taux de défaut futur (%)",
            mode='lines+markers+text',
            marker=dict(color='orange', size=10),
            line=dict(color='orange', width=2),
            text=[f"{val:.1f}%" for val in df_res['Taux de défaut']],
            textfont=dict(size=15, color='orange'),
            textposition='top center',
            hovertemplate="<b>%{x}</b><br>Taux de défaut : %{y:.2f}%<extra></extra>"
        ),
        secondary_y=True
    )

    # 3. Personnalisation de la mise en page
    max_react = df_res['Nombre de réactivations'].max()
    max_tx = df_res['Taux de défaut'].max()

    fig_defaut_dormant.update_layout(
        xaxis_title="Mois d\'activation",
        legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1),
        height=600
    )

    # Axe Y gauche (Effectifs)
    fig_defaut_dormant.update_yaxes(
        title_text="Nombre de comptes devenus actifs",
        range=[0, max_react * 1.2 if max_react > 0 else 10],
        showgrid=True,
        ticks='outside',      # <-- Petit trait de graduation vers l'extérieur
        secondary_y=False
    )

    # Axe Y droit (Taux de défaut)
    fig_defaut_dormant.update_yaxes(
        title_text="Taux de défaut (%)",
        title_font=dict(color="orange"),
        tickfont=dict(color="orange"),
        range=[0, max_tx * 1.3 if max_tx > 0 else 10],
        showgrid=False,
        secondary_y=True
    )

    # 4. Affichage Streamlit
    with col_graph :
        st.plotly_chart(fig_defaut_dormant, width='stretch')
    
    # 5. Commentaires
    with col_comment :
        st.markdown('')
        st.markdown('')
        st.markdown('')
        st.markdown(f"""
                    J'ai considéré comme compte devenant actif tout client ayant un encours à un mois donné, tout en ayant aucune activité de paiement ou d'utilisation de crédit sur tous les mois précédents.  
                    Le nombre d'activations de compte diminue en première période puis se stabilise. **Le taux de défaut futur ne semble pas être affecté par l'ancienneté récente d'un client.**  
                    *Pour rappel, le taux défaut moyen sur l'ensemble des clients du jeu de données est de **{round(df['dpnm'].sum()/df['dpnm'].count()*100,2)} %**.*  
                    Il m'est impossible de comparer avec une fermeture de comptes, des clients sont en effet avec des comptes gelés sur la période qu'il est difficile de mesurer avec les données à ma disposition.  
                    """)
    
    
    st.markdown('---')

    # Graphe Evolution de comptes actifs
    col_graph1, col_graph2 = st.columns([1,1])

        
    # 1. Liste des colonnes d'encours dans l'ordre chronologique
    colonnes_bill = [
        ('BILL_AMT6', 'M-6'),
        ('BILL_AMT5', 'M-5'),
        ('BILL_AMT4', 'M-4'),
        ('BILL_AMT3', 'M-3'),
        ('BILL_AMT2', 'M-2'),
        ('BILL_AMT1', 'M-1'),
    ]

    actifs_pct = {}
    actifs_counts = {}
    total_clients = len(df)

    # 2. Calcul du taux de comptes actifs (!= 0)
    for col, label in colonnes_bill:
        if col in df.columns:
            nb_actifs = (df[col] != 0).sum()
            prop = (nb_actifs / total_clients) * 100

            actifs_pct[label] = prop
            actifs_counts[label] = nb_actifs

    df_actifs = pd.DataFrame({
        'Mois': list(actifs_pct.keys()),
        'Pourcentage': list(actifs_pct.values()),
        'Nombre': list(actifs_counts.values()),
    })

    # 3. Création du graphique Plotly
    fig_actifs = go.Figure()

    # Ajout des barres avec les pourcentages au-dessus
    fig_actifs.add_trace(
        go.Bar(
            x=df_actifs['Mois'],
            y=df_actifs['Pourcentage'],
            text=[f'{val:.1f}%' for val in df_actifs['Pourcentage']],
            textposition='outside',
            textfont=dict(size=14, color='black'),
            marker_color='#1f77b4',  # Couleur bleue sobre et professionnelle
            customdata=df_actifs['Nombre'],
            hovertemplate=(
                '<b>%{x}</b><br>Comptes actifs : %{customdata:,}<br>Proportion :'
                ' %{y:.1f}%<extra></extra>'
            ),
        )
    )

    # Ajout des annotations à la verticale (n = ...) au milieu de chaque barre
    for _, row in df_actifs.iterrows():
        fig_actifs.add_annotation(
            x=row['Mois'],
            y=row['Pourcentage'] / 2,
            text=f"n = {int(row['Nombre']):,}".replace(',', ' '),
            showarrow=False,
            textangle=-90,  # Écriture à la verticale
            font=dict(color='white', size=16, family='Arial Black'),
        )

    # 4. Personnalisation du design et des axes
    fig_actifs.update_layout(
        xaxis_title='Mois',
        yaxis_title='Pourcentage de comptes actifs (%)',
        yaxis=dict(
            range=[0, 105],
            showgrid=True,
            gridcolor='rgba(0,0,0,0.1)',
            gridwidth=1,
        ),
        height=500
    )

    # 5. Affichage dans Streamlit
    with col_graph1 :
        st.markdown("#### Evolution de la proportion de comptes actifs (encours non nul)")
        st.plotly_chart(fig_actifs, width='stretch')
        
        
    # 6. commentaires sur les 2 graphes
    st.markdown("""
Le nombre de compte présentant un encours (y compris négatif pour les client ayant un trop perçu) augmentent chaque mois. Le nombre de comptes présentant un encours positif (somme à devoir) augmentent également chaque mois. Le taux de clients qui paient tout ou partie de leur échéance est stable sur les 6 mois.  
Cela ne signifie pas que le taux de clients à jour est stable car un client peut présenter un paiement insuffisant pour recouvrer sa dette ou son minimum d'échéance de crédit.
                """)
    st.markdown('---')
    
    
    # Graphe Evolution du taux de clients qui présentent un paiement sur encours positif
    st.markdown("#### Evolution des ratios de paiement moyen et médian par rapport à l'encours de crédit")
    # 1. Appairage chronologique : PAY_AMTn comparé à BILL_AMT(n+1)
    paires_chronologiques = [
        ('PAY_AMT5', 'BILL_AMT6', 'M-5'),
        ('PAY_AMT4', 'BILL_AMT5', 'M-4'),
        ('PAY_AMT3', 'BILL_AMT4', 'M-3'),
        ('PAY_AMT2', 'BILL_AMT3', 'M-2'),
        ('PAY_AMT1', 'BILL_AMT2', 'M-1'),
    ]

    proportions_pct = {}
    counts_dict = {}

    # 2. Calcul du taux de paiement effectif sur encours positif
    for pay_col, bill_col, label in paires_chronologiques:
        if pay_col in df.columns and bill_col in df.columns:
            subset_avec_encours = df[df[bill_col] > 0]

            if len(subset_avec_encours) > 0:
                nb_payeurs = (subset_avec_encours[pay_col] > 0).sum()
                prop = (nb_payeurs / len(subset_avec_encours)) * 100

                proportions_pct[label] = prop
                counts_dict[label] = nb_payeurs

    df_pay = pd.DataFrame({
        'Mois': list(proportions_pct.keys()),
        'Pourcentage': list(proportions_pct.values()),
        'Nombre': list(counts_dict.values()),
    })

    # 3. Création du graphique Plotly
    fig_pay = go.Figure()

    # Barres principales avec le pourcentage au-dessus
    fig_pay.add_trace(
        go.Bar(
            x=df_pay['Mois'],
            y=df_pay['Pourcentage'],
            text=[f'{val:.1f}%' for val in df_pay['Pourcentage']],
            textposition='outside',
            textfont=dict(size=14, color='black'),
            marker_color="#2ca02c", 
            customdata=df_pay['Nombre'],
            hovertemplate=(
                '<b>%{x}</b><br>Payeurs effectifs : %{customdata:,}<br>Taux de'
                ' paiement : %{y:.1f}%<extra></extra>'
            ),
        )
    )

    # Ajout du nombre d'individus à la verticale (n = ...) au centre des barres
    for _, row in df_pay.iterrows():
        fig_pay.add_annotation(
            x=row['Mois'],
            y=row['Pourcentage'] / 2,
            text=f"n = {int(row['Nombre']):,}".replace(',', ' '),
            showarrow=False,
            textangle=-90,  # Texte affiché à la verticale
            font=dict(color='white', size=16, family='Arial Black'),
        )

    # 4. Configuration de la mise en page
    fig_pay.update_layout(
        xaxis_title='Mois',
        yaxis_title='Pourcentage de paiements effectifs (%)',
        yaxis=dict(
            range=[0, 105],
            showgrid=True,
            gridcolor='rgba(0,0,0,0.1)',
            gridwidth=1,
        ),
        height=500,
    )

    # 5. Affichage dans Streamlit
    with col_graph2 :
        st.markdown("#### Evolution du taux de clients présentant un paiement sur encours positif")
        st.plotly_chart(fig_pay, width='stretch')
        
        
    # GRAPHES EVOLUTION DES RATIOS DE PAIEMENT SUR DETTE MOYEN ET MEDIAN

    col_graph1, col_graph2 = st.columns([1, 1])

    # 1. Définition des paires de colonnes et des étiquettes de M-5 à M-1
    mapping_ratios = [
        ('ratio_PAY_BILL5', 'M-5'),
        ('ratio_PAY_BILL4', 'M-4'),
        ('ratio_PAY_BILL3', 'M-3'),
        ('ratio_PAY_BILL2', 'M-2'),
        ('ratio_PAY_BILL1', 'M-1'),
    ]

    # Filtrage des colonnes présentes dans le DataFrame
    colonnes_actives = [
        col for col, label in mapping_ratios if col in df.columns
    ]
    labels_x = [label for col, label in mapping_ratios if col in df.columns]

    if len(colonnes_actives) > 0:

    # =========================================================================
    # 1. GRAPHIQUE BLEU : RATIO MOYEN
    # =========================================================================
        moyennes = ratios_affichables(df, colonnes_actives).mean()

        fig_ratio = go.Figure()
        fig_ratio.add_trace(
            go.Scatter(
                x=labels_x,
                y=moyennes.values,
                mode='lines+markers+text',
                text=[f'{val:.2f}' for val in moyennes.values],
                textposition='top center',
                textfont=dict(size=14, color='black'),
                marker=dict(size=9, color='#1f77b4'),  # Bleu
                line=dict(width=2.5, color='#1f77b4'),
                hovertemplate=(
                    '<b>%{x}</b><br>Ratio de paiement moyen :'
                    ' %{y:.2f}%<extra></extra>'
                ),
            )
        )

        max_val_moy = moyennes.max()
        min_val_moy = moyennes.min()
        marge_moy = (
            (max_val_moy - min_val_moy) * 0.25 if max_val_moy != min_val_moy else 0.05
        )

        fig_ratio.update_layout(
            title=dict(
                text=(
                    '<b>Évolution du ratio moyen (Paiement / Facture'
                    ' précédente)</b>'
                ),
                font=dict(size=14),
            ),
            xaxis_title='Mois (Période relative)',
            yaxis_title='Ratio de paiement moyen (%)',
            yaxis=dict(
                range=[min_val_moy - marge_moy, max_val_moy + marge_moy],
                showgrid=True,
                gridcolor='rgba(0,0,0,0.1)',
                gridwidth=1,
            ),
            height=500,
        )

        with col_graph1:
            st.plotly_chart(fig_ratio, width='stretch')

        # =========================================================================
        # 2. GRAPHIQUE VIOLET : RATIO MÉDIAN
        # =========================================================================
        medianes = ratios_affichables(df, colonnes_actives).median()

        fig_medianes = go.Figure()
        fig_medianes.add_trace(
            go.Scatter(
                x=labels_x,
                y=medianes.values,
                mode='lines+markers+text',
                text=[f'{val:.2f}' for val in medianes.values],
                textposition='top center',
                textfont=dict(size=14, color='black'),
                marker=dict(size=9, color='#8e44ad'),  # Violet
                line=dict(width=2.5, color='#8e44ad'),
                hovertemplate=(
                    '<b>%{x}</b><br>Ratio de paiement médian :'
                    ' %{y:.2f}%<extra></extra>'
                ),
            )
        )

        max_val_med = medianes.max()
        min_val_med = medianes.min()
        marge_med = (
            (max_val_med - min_val_med) * 0.25 if max_val_med != min_val_med else 0.05
        )

        fig_medianes.update_layout(
            title=dict(
                text=(
                    '<b>Évolution du ratio médian (Paiement / Facture'
                    ' précédente)</b>'
                ),
                font=dict(size=14),
            ),
            xaxis_title='Mois',
            yaxis_title='Ratio de paiement médian (%)',
            yaxis=dict(
                range=[min_val_med - marge_med, max_val_med + marge_med],
                showgrid=True,
                gridcolor='rgba(0,0,0,0.1)',
                gridwidth=1,
            ),
            height=500,
        )

        with col_graph2:
            st.plotly_chart(fig_medianes, width='stretch')

    else:
        st.warning("Aucune des colonnes de ratios n'a été trouvée dans le dataset.")
