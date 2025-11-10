import streamlit as st
from agents.git_clone_agent import run_git_clone_agent
from agents.dockerfile_agent import run_dockerfile_agent
from agents.build_publish_agent import run_build_push_agent
import os
import json
from dotenv import load_dotenv
# Load environment variables from .env
load_dotenv()

st.set_page_config(page_title="AI Application Onboarding", page_icon="🚀", layout="centered")

st.title("🤖 AI Application Onboarding Platform")
st.markdown("Seamlessly onboard your applications into Kubernetes!")

# -------------------------------
# Step 1: Get Inputs
# -------------------------------
st.header("1️⃣ Repository Details")

git_url = st.text_input("🔗 Enter your Git Repository URL", placeholder="https://github.com/org/sample-app.git")
app_type = st.selectbox("⚙️ Select Application Type", ["Select Type", "NodeJS", "Python", "Java", ".NET"], index=0)

# -------------------------------
# Step 2: Clone Button
# -------------------------------
if st.button("📦 Clone Repository"):
    if not git_url or app_type == "Select Type":
        st.warning("⚠️ Please provide both Git URL and Application Type.")
    else:
        with st.spinner("🧠 Cloning repository... please wait..."):
            try:
                result = run_git_clone_agent(git_url, app_type)
                st.success("✅ Clone Completed Successfully!")
                for output in result:
                    st.text_area("Agent Output", value=output, height=150)
                    # Extract workspace path
                    workspace_path = output.get('workspace_path', None)
                    st.session_state.workspace_path = workspace_path
            except Exception as e:
                st.error(f"❌ Clone Failed: {e}")


st.header("2️⃣ Dockerfile Generation")

if st.button("🛠️ Generate Dockerfile"):
    if not git_url or app_type == "Select Type":
        st.warning("⚠️ Please provide Git URL and Application Type first.")
    else:
        with st.spinner("Generating Dockerfile..."):
            try:
                workspace_path = st.session_state.get("workspace_path", None)
                st.code(workspace_path, language="dockerfile")
                dockerfile_path = run_dockerfile_agent(app_type, workspace_path)  # workspace_path from clone step
                st.success(f"✅ Dockerfile saved at: {dockerfile_path}")
                st.code(open(dockerfile_path).read(), language="dockerfile")
            except Exception as e:
                st.error(f"❌ Dockerfile generation failed: {e}")

# ===========================================
# Step 3: Build & Publish Image
# ===========================================
st.header("3 Build & Publish Docker Image")

registry_input = st.text_input("🏷️ Enter Image Tag (e.g., shan5a6/myapp:v1.0.0)")
workspace_path = st.session_state.get("workspace_path", None)

if st.button("🚀 Build & Publish Image"):
    if not registry_input or not workspace_path:
        st.warning("⚠️ Please provide Image Tag and ensure the repo is cloned.")
    else:
        with st.spinner("Building and pushing Docker image..."):
            try:
                result = run_build_push_agent(app_type, registry_input, workspace_path)
                st.success("✅ Build & Publish Completed!")
            except Exception as e:
                st.error(f"❌ Build & Publish Failed: {e}")


st.markdown("---")
st.caption("© 2025 AI DevOps Onboarding | Powered by LangChain + Streamlit")
