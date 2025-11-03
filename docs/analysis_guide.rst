Analysis Guide
==============

This guide provides detailed workflows for running phylogenetic analyses in PhyloForester.

Overview
--------

PhyloForester supports three main approaches to phylogenetic tree reconstruction:

1. **Parsimony**: Finds trees minimizing character state changes
2. **Maximum Likelihood**: Finds trees maximizing probability of observed data
3. **Bayesian Inference**: Estimates posterior probability distribution of trees

Each method has strengths and is suited for different datasets and research questions.

Choosing an Analysis Method
----------------------------

Parsimony
~~~~~~~~~

**Best for:**

- Morphological data
- Small to medium datasets (<100 taxa)
- Discrete character states
- Pedagogical purposes

**Advantages:**

- Fast computation
- No model assumptions
- Easy to interpret

**Limitations:**

- Assumes equal rates across branches
- Can be inconsistent with long branches
- No statistical framework for support

Maximum Likelihood
~~~~~~~~~~~~~~~~~~

**Best for:**

- Molecular data (DNA/protein sequences)
- Large datasets (100+ taxa)
- Model-based inference

**Advantages:**

- Statistical framework
- Model flexibility
- Bootstrap support values

**Limitations:**

- Computationally intensive
- Requires model selection
- Less suited for morphology

Bayesian Inference
~~~~~~~~~~~~~~~~~~

**Best for:**

- Complex evolutionary models
- Integrating prior information
- Uncertainty quantification

**Advantages:**

- Full probabilistic framework
- Posterior probabilities
- Handles complex models well

**Limitations:**

- Very computationally intensive
- Convergence assessment required
- Prior specification needed

Parsimony Workflow
------------------

Step 1: Prepare Data
~~~~~~~~~~~~~~~~~~~~

Ensure your datamatrix:

- Has clear character definitions
- Minimal missing data (``?``)
- Proper inapplicable coding (``-``)

Step 2: Create Parsimony Analysis
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Right-click datamatrix → **New Analysis** → **Parsimony**
2. Configure parameters:

   .. code-block:: text

      Replicates: 100
      Hold: 1000
      TBR: Yes (tree bisection-reconnection)
      Mult: 10 (random addition sequences)

Step 3: Run Analysis
~~~~~~~~~~~~~~~~~~~~~

1. Click **Start Analysis**
2. TNT performs heuristic search
3. Progress shown as percentage
4. Typical runtime: seconds to minutes

Step 4: Examine Results
~~~~~~~~~~~~~~~~~~~~~~~~

Check the **Log** tab for:

- Number of trees found
- Tree length (total character changes)
- Consistency Index (CI)
- Retention Index (RI)

**Trees Tab:**

- Strict consensus tree shown
- Bootstrap values (if requested)
- Branch lengths (steps)

Maximum Likelihood Workflow
----------------------------

Step 1: Prepare Data
~~~~~~~~~~~~~~~~~~~~

For DNA sequences:

- Aligned sequences required
- IUPAC ambiguity codes supported
- Gap coding as missing (``?``) or 5th state

Step 2: Model Selection
~~~~~~~~~~~~~~~~~~~~~~~~

IQTree can auto-detect best model:

1. Enable **Auto-detect model**
2. IQTree tests all standard models
3. Best model selected by AIC/BIC

Or specify model manually:

- **JC69**: Jukes-Cantor (equal rates)
- **K80/K2P**: Kimura 2-parameter (transitions/transversions)
- **HKY**: Has​egawa-Kishino-Yano
- **GTR**: General time reversible (most parameters)

Step 3: Create ML Analysis
~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Right-click datamatrix → **New Analysis** → **Maximum Likelihood**
2. Configure:

   .. code-block:: text

      Model: Auto-detect
      Bootstrap: 1000
      Algorithm: Standard

Step 4: Run Analysis
~~~~~~~~~~~~~~~~~~~~~

1. Click **Start Analysis**
2. Model testing phase (if auto-detect)
3. Tree search phase
4. Bootstrap phase (if enabled)
5. Typical runtime: minutes to hours

Step 5: Interpret Results
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Best Tree:**

- Maximum likelihood tree topology
- Branch lengths (substitutions/site)
- Log-likelihood score

**Bootstrap Support:**

- Values 0-100 on nodes
- ≥70 generally considered significant
- ≥95 strong support

Bayesian Workflow
-----------------

Step 1: Prepare Data
~~~~~~~~~~~~~~~~~~~~

Similar to ML, but Bayesian is more flexible:

- Can handle complex partitions
- Morphology + molecules combined
- Clock models for dating

Step 2: Set Priors
~~~~~~~~~~~~~~~~~~

**Substitution Model:**

- Often use GTR+Γ for DNA
- Mk model for morphology

**Tree Prior:**

- Uniform (default)
- Birth-death process
- Yule model

**Branch Length Prior:**

- Exponential distribution
- Compound Dirichlet

Step 3: Configure MCMC
~~~~~~~~~~~~~~~~~~~~~~~

1. Right-click datamatrix → **New Analysis** → **Bayesian**
2. Set parameters:

   .. code-block:: text

      Generations: 1,000,000
      Sample frequency: 1000
      Burnin: 0.25 (25%)
      Chains: 4 (2 heated)

**Short run for testing:**

.. code-block:: text

   Generations: 100,000
   Sample: 100
   Burnin: 0.25

**Standard run:**

.. code-block:: text

   Generations: 10,000,000
   Sample: 1000
   Burnin: 0.25

Step 4: Run Analysis
~~~~~~~~~~~~~~~~~~~~~

1. Click **Start Analysis**
2. MrBayes runs MCMC chains
3. Monitor:
   - Average standard deviation of split frequencies (should approach 0.01)
   - Potential Scale Reduction Factor (should approach 1.0)
4. Typical runtime: hours to days

Step 5: Assess Convergence
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Check the **Log** for:

- **ASDSF < 0.01**: Chains converged
- **ESS > 200**: Sufficient sampling
- Stable log-likelihood traces

If not converged:

- Run more generations
- Increase sample frequency
- Simplify model

Step 6: Examine Posterior
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Consensus Tree:**

- 50% majority rule consensus
- Posterior probabilities on nodes
- ≥0.95 generally considered strong support

**Credible Sets:**

- 95% credible set of trees
- Topology uncertainty quantified

Character Mapping
-----------------

After obtaining trees, map characters to visualize evolution.

Fitch Parsimony Mapping
~~~~~~~~~~~~~~~~~~~~~~~~

PhyloForester uses Fitch's algorithm for ancestral state reconstruction.

1. Open analysis with trees
2. Select a tree in **Trees** tab
3. Click **Map Character**
4. Select character from list
5. Tree shows:
   - Ancestral states at nodes
   - State changes on branches (synapomorphies)
   - Colored by state

Interpreting Mapped Trees
~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Node labels**: Reconstructed ancestral states
- **Branch annotations**: Character changes
- **Colors**: Different states
- **Ambiguous**: Multiple optimal reconstructions shown

Use cases:

- Identify evolutionary transitions
- Locate homoplasy (parallel/convergent evolution)
- Support morphological hypotheses

Comparing Analyses
------------------

It's valuable to compare results across methods.

Topology Comparison
~~~~~~~~~~~~~~~~~~~

1. Run multiple analysis types on same datamatrix
2. Compare tree topologies visually
3. Note areas of agreement/disagreement

Key questions:

- Do methods agree on major clades?
- Where do topologies differ?
- Are differences in weakly supported regions?

Support Value Comparison
~~~~~~~~~~~~~~~~~~~~~~~~~

- **Parsimony**: Bootstrap (if run)
- **ML**: Bootstrap percentages
- **Bayesian**: Posterior probabilities

Generally:

- Bayesian PP ≥ 0.95 ≈ ML bootstrap ≥ 70%
- Bayesian tends to give higher values
- ML bootstrap more conservative

Troubleshooting Analyses
-------------------------

Analysis Won't Start
~~~~~~~~~~~~~~~~~~~~

**Check:**

1. External software path set correctly (Preferences)
2. Software executable has permissions
3. Datamatrix not empty
4. No special characters in names

Analysis Fails Immediately
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Check:**

1. Log tab for error messages
2. Datamatrix format correct
3. Missing data not excessive
4. Character definitions valid

Analysis Runs Forever
~~~~~~~~~~~~~~~~~~~~~~

**For Bayesian:**

- May take days - check convergence diagnostics
- Consider reducing generations for testing

**For ML:**

- Large datasets take time
- Consider reducing bootstrap replicates temporarily

**For Parsimony:**

- Usually fast; if slow, reduce Hold parameter

Poor Support Values
~~~~~~~~~~~~~~~~~~~

Common reasons:

- Insufficient data
- Conflicting signal
- Model misspecification
- Need more bootstrap replicates

Solutions:

- Add more characters/taxa
- Try different models
- Increase replicates
- Partition data

Best Practices
--------------

Data Preparation
~~~~~~~~~~~~~~~~

1. Carefully define characters
2. Minimize missing data
3. Check for typos in taxon names
4. Validate alignment (for sequences)

Parameter Selection
~~~~~~~~~~~~~~~~~~~

1. Start with default/recommended values
2. Do quick test runs first
3. Increase rigor for final analyses
4. Document all parameters used

Quality Control
~~~~~~~~~~~~~~~

1. Always check log files
2. Verify convergence (Bayesian)
3. Compare multiple runs
4. Examine support values critically

Publication
~~~~~~~~~~~

When publishing, report:

- Software versions
- All parameter settings
- Run statistics (length, likelihood, etc.)
- Support measures
- Convergence diagnostics (Bayesian)

Next Steps
----------

- See :doc:`user_guide` for general PhyloForester usage
- See :doc:`troubleshooting` for specific issues
- See :doc:`developer_guide` for advanced customization
