import streamlit as st
import os
import time
from pathlib import Path
from dotenv import load_dotenv
from crew import Marketresearcher
import traceback

# Load environment variables from project root
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)


def check_api_keys():
    required_vars = ['SERPER_API_KEY', 'OPENROUTER_API_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    return missing_vars


def _move_generated_files_to_output_streamlit(crew_instance, company_name: str):
    """Move any generated files from current directory to proper output directory for Streamlit"""
    import shutil
    current_dir = Path(".")
    
    # List of potential output files that might be generated
    potential_files = [
        "final_proposal.md",
        "comprehensive_ai_proposal.md", 
        "proposal.md",
        "report.md"
    ]
    
    moved_files = []
    
    for filename in potential_files:
        file_path = current_dir / filename
        if file_path.exists():
            # Generate unique destination path
            dest_path = crew_instance.output_manager.get_report_path(company_name, filename.replace('.md', ''))
            
            try:
                # Move file to output directory (silently)
                shutil.move(str(file_path), str(dest_path))
                moved_files.append(dest_path)
            except Exception as e:
                # Only show error messages, not success messages
                st.warning(f"⚠️ Failed to move {filename}: {e}")
    
    # Only show a summary message if files were moved
    if moved_files:
        st.success(f"📊 Generated {len(moved_files)} report file(s) successfully")


def main():
    st.set_page_config(
        page_title="🔬 Strategic AI Research Assistant",
        page_icon="🧠",
        layout="wide"
    )

    st.title("🔬 Strategic AI Research Assistant")
    st.markdown("*Powered by CrewAI + Streamlit*")

    # Session state setup
    if 'research_completed' not in st.session_state:
        st.session_state.research_completed = False
    if 'research_result' not in st.session_state:
        st.session_state.research_result = None
    if 'research_error' not in st.session_state:
        st.session_state.research_error = None

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        missing_vars = check_api_keys()

        if missing_vars:
            st.error("❌ Missing API Keys")
            for var in missing_vars:
                st.code(f"{var}=your_api_key_here")
        else:
            st.success("✅ All API Keys Configured")

        st.header("🧠 Multi-Agent Team")
        st.markdown("""
        - 🔍 **Industry Researcher**
        - 🧠 **Competitor Analyst**
        - ✍️ **Proposal Writer**
        """)

    # Input
    st.header("🏢 Enter Company Name for AI Research")
    company = st.text_input("Company Name", placeholder="e.g., BNY Mellon")

    if st.button("🚀 Run Research", type="primary", disabled=bool(missing_vars)):
        if not company.strip():
            st.error("Please enter a valid company name")
        else:
            st.session_state.research_completed = False
            st.session_state.research_result = None
            st.session_state.research_error = None

            with st.container():
                st.info("🔄 Running CrewAI Agents...")
                progress = st.progress(0)
                for i in range(101):
                    progress.progress(i)
                    time.sleep(0.02)

            try:
                # Create crew instance and set company name for dynamic output paths
                crew_instance = Marketresearcher()
                crew_instance.set_company_name(company)
                
                # Run research
                result = crew_instance.crew().kickoff(inputs={"company": company})
                st.session_state.research_result = result
                st.session_state.research_completed = True
                st.session_state.research_error = None
                
                # Post-process: Move generated files to proper output directory
                _move_generated_files_to_output_streamlit(crew_instance, company)
                
                # Save execution metadata (silently)
                metadata = {
                    "company": company,
                    "execution_status": "completed",
                    "interface": "streamlit",
                    "agents_used": ["industry_researcher", "competitor_researcher", "impact_writer", "use_case_analyst", "proposal_writer"]
                }
                crew_instance.output_manager.save_metadata(company, metadata)
            except Exception as e:
                st.session_state.research_error = f"{str(e)}\n\nFull traceback:\n{traceback.format_exc()}"
                st.session_state.research_completed = True

    # Results
    if st.session_state.research_completed:
        st.header("📄 Final Proposal")

        if st.session_state.research_error:
            st.error("❌ Error occurred:")
            st.code(st.session_state.research_error, language="text")
        elif st.session_state.research_result:
            st.success("✅ Research Completed!")
            
            # Display the result directly from CrewAI
            if hasattr(st.session_state.research_result, 'raw'):
                content = st.session_state.research_result.raw
            else:
                content = str(st.session_state.research_result)
            
            st.markdown("### 📊 Research Results:")
            st.markdown(content)
            
            # Download button
            st.download_button(
                label="📥 Download Research Report",
                data=content,
                file_name=f"market_research_{company.replace(' ', '_').lower()}.md",
                mime="text/markdown"
            )
            
            # Also check for any generated files
            filepath = "proposal.md"
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    file_content = f.read()
                st.markdown("### 📄 Generated Proposal File:")
                st.markdown(file_content)
        else:
            st.warning("⚠️ No results to display.")

    st.markdown("---")
    st.markdown("*Built with ❤️ using CrewAI, Streamlit, and OpenRouter LLMs*")


if __name__ == "__main__":
    main()
