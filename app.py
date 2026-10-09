import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import io

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Virtual Triple Beam Balance Lab",
    page_icon="⚖️",
    layout="centered"
)

# --- LOAD LAB DATA FROM CSV ---
DEFAULT_OBJECTS = {
    "Copper Cylinder 🪙": {"actual_mass": 145.30, "description": "A dense metallic cylinder used for density verification."},
    "Wooden Block 🪵": {"actual_mass": 62.45, "description": "A lightweight pine block. Keep away from water!"},
    "Unknown Powdery Substance (in 50g Beaker) 🧪": {"actual_mass": 118.85, "description": "Total mass of the chemical inside a 50.00g glass beaker."},
    "Mystery Antique Coin 🪙": {"actual_mass": 12.15, "description": "A worn-out historical coin. What is it made of?"}
}

try:
    df_objects = pd.read_csv("lab_objects.csv")
    LAB_OBJECTS = {}
    for _, row in df_objects.iterrows():
        LAB_OBJECTS[row['object_name']] = {
            "actual_mass": float(row['actual_mass']),
            "description": row['description']
        }
except Exception:
    LAB_OBJECTS = DEFAULT_OBJECTS

# --- APP TITLE & INTRO ---
st.title("⚖️ Visual Triple Beam Balance Lab")
st.markdown("Welcome to the interactive mass measurement laboratory. Review the student manual below and read the mechanical beams manually to determine mass.")

# --- STUDENT SELF-DIRECTED LAB GUIDE ---
with st.expander("📖 Student Lab Manual & Instructions (Read First)", expanded=True):
    st.markdown("""
    ### 🎯 Objective
    To learn how to properly calibrate, adjust, and visually read a mechanical triple beam balance to determine the precise mass of unknown objects.

    ### 🔬 Background & Theory
    A triple beam balance determines mass by balancing an unknown object on a pan against known reference weights (riders) sliding across three graduated beams:
    1. **Hundreds Beam:** Increments of 100g (up to 500g).
    2. **Tens Beam:** Increments of 10g (up to 100g).
    3. **Ones / Tenths Beam:** Increments of 1g down to 0.05g.

    ### 📝 Step-by-Step Procedure for Students
    1. **Zero Calibration (Step 1):** Ensure all riders are set to zero. Use the calibration knob to align the pointer exactly with the `0.00` index mark.
    2. **Object Placement (Step 2):** Select your unknown object from the dropdown menu to place it on the balance pan.
    3. **Manual Rider Adjustment & Reading (Step 3):** 
       * Use the manual sliders below to adjust the physical position of the riders on the balance beams.
       * **Inspect the visual scale display yourself** to read where the riders are positioned and watch the pointer alignment.
    4. **Data Recording (Step 4):** Sum the values from your visual inspection of the beams, enter your final reading, and export your lab notebook entry as a CSV.
    """)

st.markdown("---")

# --- STEP 1: PRE-LAB CALIBRATION ---
st.header("Step 1: Calibration (Zeroing the Scale)")
st.info("Before placing an object on the scale, the balance pointer must line up exactly with **0.00**.")

calibration_error = st.slider(
    "Zero Adjustment Knob (Calibrate the balance pointer):", 
    min_value=-2.0, max_value=2.0, value=1.2, step=0.1,
    help="Turn this knob until the alignment pointer below hits exactly 0.00 when riders are at zero."
)

# --- STEP 2: SELECT LAB OBJECT ---
st.header("Step 2: Choose Your Object")
selected_object_name = st.selectbox("Select an object to place on the pan:", list(LAB_OBJECTS.keys()))
object_info = LAB_OBJECTS[selected_object_name]

st.markdown(f"**Object Description:** *{object_info['description']}*")

# --- STEP 3: MANUAL RIDER CONTROLS ---
st.header("Step 3: Adjust the Riders & Read Manually")
st.write("Position the riders along the beams below, then **visually read the scale display** to determine your total mass.")

col1, col2, col3 = st.columns(3)

with col1:
    rider_100 = st.slider("Hundreds Beam (g)", min_value=0, max_value=500, value=0, step=100)
with col2:
    rider_10 = st.slider("Tens Beam (g)", min_value=0, max_value=100, value=0, step=10)
with col3:
    rider_1 = st.slider("Ones / Tenths Beam (g)", min_value=0.00, max_value=10.00, value=0.00, step=0.05)

current_rider_sum = rider_100 + rider_10 + rider_1
target_mass_with_calibration = object_info["actual_mass"] + calibration_error
pointer_deflection = current_rider_sum - target_mass_with_calibration

# --- STEP 4: INTERACTIVE VISUAL LAB COMPONENT ---
st.subheader("Live Visual Balance Display")

clamped_deflection = max(-5.0, min(5.0, pointer_deflection))
angle = -clamped_deflection * 3  

if abs(pointer_deflection) < 0.02:
    status_color = "#2ecc71"  
    status_msg = "🎯 BALANCED! Pointer is at exactly 0.00"
elif pointer_deflection > 0:
    status_color = "#f39c12"  
    status_msg = f"🔼 TOO HEAVY (Riders outweigh object by +{pointer_deflection:.2f}g)"
else:
    status_color = "#e74c3c"  
    status_msg = f"🔽 TOO LIGHT (Object outweighs riders by {pointer_deflection:.2f}g)"

pan_emoji = selected_object_name.split()[-1] if len(selected_object_name.split()) > 0 else "📦"

balance_html = f"""
<div style="background-color: #1e1e1e; padding: 20px; border-radius: 12px; font-family: sans-serif; color: white; border: 2px solid {status_color}; text-align: center;">
    <div style="font-size: 16px; font-weight: bold; color: {status_color}; margin-bottom: 15px;">
        {status_msg}
    </div>
    
    <div style="position: relative; width: 100%; height: 200px; margin: 0 auto; overflow: hidden; background: #252526; border-radius: 8px;">
        
        <!-- Fixed Central Fulcrum -->
        <div style="position: absolute; bottom: 0; left: 30%; width: 40px; height: 110px; background: #555; clip-path: polygon(50% 0%, 0% 100%, 100% 100%); z-index: 2;"></div>
        <div style="position: absolute; bottom: 0; left: 0; width: 100%; height: 15px; background: #333; z-index: 1;"></div>
        
        <!-- Fixed Zero Indicator Rest -->
        <div style="position: absolute; top: 75px; right: 20px; width: 30px; height: 30px; border-left: 3px solid white; border-top: 1px solid #777; border-bottom: 1px solid #777;">
            <div style="position: absolute; top: 13px; left: 0; width: 12px; height: 2px; background: #2ecc71; font-size: 9px; line-height: 2px; padding-left: 15px; color: #2ecc71;">0.00</div>
        </div>

        <!-- Dynamic Tilting Beam Mechanism -->
        <div style="position: absolute; top: 85px; left: 10%; width: 80%; height: 12px; background: linear-gradient(90deg, #aaa, #ddd); transform-origin: 25% 50%; transform: rotate({angle}deg); transition: transform 0.3s ease-out; z-index: 3; border-radius: 4px;">
            
            <!-- Left Side: Measurement Pan -->
            <div style="position: absolute; top: -50px; left: 5%; width: 60px; height: 60px; background: #888; border-radius: 50% 50% 0 0; border: 3px solid #ccc; transform: rotate({-angle}deg); transition: transform 0.3s ease-out; transform-origin: 50% 0%;">
                <div style="font-size: 24px; margin-top: 15px; text-shadow: 1px 1px 2px black;">
                    {pan_emoji}
                </div>
            </div>
            
            <!-- Center Right: Slider Positions -->
            <div style="position: absolute; top: -15px; left: 35%; width: 55%; height: 10px; border-top: 2px dashed #666; border-bottom: 2px dashed #666;">
                <div style="position: absolute; left: {min(90, (rider_100/500)*100)}%; top: -6px; width: 10px; height: 10px; background: red; border-radius: 2px;"></div>
                <div style="position: absolute; left: {min(90, (rider_10/100)*100)}%; top: -1px; width: 8px; height: 8px; background: blue; border-radius: 2px;"></div>
                <div style="position: absolute; left: {min(90, (rider_1/10)*100)}%; top: 4px; width: 6px; height: 6px; background: silver; border-radius: 1px;"></div>
            </div>
            
            <!-- Far Right Tip: Pointer Arrow -->
            <div style="position: absolute; top: 3px; right: -5px; width: 25px; height: 4px; background: #e74c3c; clip-path: polygon(0 0, 100% 50%, 0 100%);"></div>
        </div>
    </div>
</div>
"""
components.html(balance_html, height=260)

# --- STEP 5: MANUAL READING SUBMISSION & DATA EXPORT ENGINE ---
st.header("Step 4: Record Your Manual Reading")
st.write("Examine the beam positions manually, calculate the total mass from your visual reading, and log it below.")

user_guess = st.number_input("Enter your manually read mass value (g):", min_value=0.00, step=0.01, format="%.2f")

if st.button("Check My Lab Notebook Reading"):
    if abs(calibration_error) > 0.05 and abs(user_guess - object_info["actual_mass"]) < 0.1:
        st.error("❌ **Measurement Error:** Your reading looks close, but you forgot to calibrate your scale to 0.00 first! Your data contains systematic calibration error.")
    elif abs(user_guess - object_info["actual_mass"]) <= 0.05:
        st.balloons()
        st.success(f"🎉 **Correct!** You successfully measured the {selected_object_name} at **{object_info['actual_mass']:.2f}g**.")
        
        notebook_data = pd.DataFrame([{
            "Selected Object": selected_object_name,
            "Calibration Offset Used": calibration_error,
            "Hundreds Beam Setting (g)": rider_100,
            "Tens Beam Setting (g)": rider_10,
            "Ones Beam Setting (g)": rider_1,
            "Manually Logged Final Reading (g)": user_guess,
            "Status": "Passed Verification"
        }])
        
        csv_buffer = io.StringIO()
        notebook_data.to_csv(csv_buffer, index=False)
        csv_bytes = csv_buffer.getvalue().encode('utf-8')
        
        st.download_button(
            label="💾 Download Lab Notebook Entry (.CSV)",
            data=csv_bytes,
            file_name="completed_lab_entry.csv",
            mime="text/csv"
        )
    else:
        st.error(f"❌ **Incorrect Reading:** Your recorded mass of {user_guess:.2f}g is outside acceptable variance. Re-examine the beam positions manually until the balance pointer rests at 0.00.")