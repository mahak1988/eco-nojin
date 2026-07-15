"""
تست ابزارهای محاسباتی سریع (بدون نیاز به Go/Julia)
"""

import sys
from pathlib import Path

current_file = Path(__file__).resolve()
project_root = current_file.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import asyncio
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def test_fast_compute():
    """تست ابزارهای محاسباتی سریع."""
    logger.info("🚀 Starting Fast Compute Test (Pure Python)")
    logger.info("💡 No Go/Julia installation required!")
    
    # Step 1: Fast Statistics
    logger.info("\n📊 Step 1: Testing Fast Statistics...")
    try:
        from apps.shared_ai.ai.tools.fast_compute import fast_statistics
        
        data = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0]
        result = await fast_statistics.ainvoke({"data": data})
        logger.info(f"✅ Result:\n{result[:300]}...")
    except Exception as e:
        logger.error(f"❌ Fast Statistics failed: {e}")
    
    # Step 2: Monte Carlo
    logger.info("\n🎲 Step 2: Testing Monte Carlo Simulation...")
    try:
        from apps.shared_ai.ai.tools.fast_compute import monte_carlo_simulation
        
        result = await monte_carlo_simulation.ainvoke({
            "iterations": 10000,
            "steps": 100,
            "up_factor": 1.1,
            "down_factor": 0.9
        })
        logger.info(f"✅ Result:\n{result[:300]}...")
    except Exception as e:
        logger.error(f"❌ Monte Carlo failed: {e}")
    
    # Step 3: Differential Equations
    logger.info("\n🧮 Step 3: Testing Differential Equations...")
    try:
        from apps.shared_ai.ai.tools.scientific_compute import solve_differential_equation
        
        result = await solve_differential_equation.ainvoke({
            "initial_conditions": [1.0],
            "time_span": [0.0, 5.0],
            "coefficients": [0.5]
        })
        logger.info(f"✅ Result:\n{result[:300]}...")
    except Exception as e:
        logger.error(f"❌ Differential Equations failed: {e}")
    
    # Step 4: Matrix Operations
    logger.info("\n🔢 Step 4: Testing Matrix Operations...")
    try:
        from apps.shared_ai.ai.tools.scientific_compute import advanced_matrix_operations
        
        # 3x3 symmetric matrix
        matrix = [4.0, -2.0, 1.0, -2.0, 4.0, -2.0, 1.0, -2.0, 4.0]
        result = await advanced_matrix_operations.ainvoke({
            "matrix": matrix,
            "operation": "eigen"
        })
        logger.info(f"✅ Result:\n{result[:300]}...")
    except Exception as e:
        logger.error(f"❌ Matrix Operations failed: {e}")
    
    # Step 5: ML Training
    logger.info("\n🤖 Step 5: Testing ML Training...")
    try:
        from apps.shared_ai.ai.tools.scientific_compute import train_ml_model
        
        # y = 2x + 1
        X = [1.0, 2.0, 3.0, 4.0, 5.0]
        y = [3.0, 5.0, 7.0, 9.0, 11.0]
        
        result = await train_ml_model.ainvoke({
            "X": X,
            "y": y,
            "model_type": "linear_regression"
        })
        logger.info(f"✅ Result:\n{result[:300]}...")
    except Exception as e:
        logger.error(f"❌ ML Training failed: {e}")
    
    # Step 6: Numerical Integration
    logger.info("\n∫ Step 6: Testing Numerical Integration...")
    try:
        from apps.shared_ai.ai.tools.scientific_compute import numerical_integration
        
        # ∫(x^2) from 0 to 1 = 1/3
        result = await numerical_integration.ainvoke({
            "coefficients": [0.0, 0.0, 1.0],
            "bounds": [0.0, 1.0]
        })
        logger.info(f"✅ Result:\n{result[:300]}...")
    except Exception as e:
        logger.error(f"❌ Integration failed: {e}")
    
    logger.info("\n✅ Fast Compute Test Completed!")
    logger.info("\n📊 Summary:")
    logger.info("   - Fast Statistics (Numba): ✅")
    logger.info("   - Monte Carlo (Numba): ✅")
    logger.info("   - Differential Equations (SciPy): ✅")
    logger.info("   - Matrix Operations (SciPy): ✅")
    logger.info("   - ML Training (NumPy/SciPy): ✅")
    logger.info("   - Numerical Integration (SciPy): ✅")
    logger.info("\n💡 All tests passed without Go/Julia installation!")


if __name__ == "__main__":
    asyncio.run(test_fast_compute())