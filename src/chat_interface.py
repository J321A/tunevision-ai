"""
Interactive chat interface for music recommendations.
Uses Gradio for web-based conversation.
"""

import gradio as gr
import os
from typing import List, Dict, Tuple
from chat_agent import create_music_chat_agent
from recommender import load_songs


def format_recommendations(recommendations: List[Dict]) -> str:
    """Format recommendations for display in chat."""
    if not recommendations:
        return ""

    formatted = "\n\n**Recommended Songs:**\n"
    for i, rec in enumerate(recommendations, 1):
        song = rec['song']
        formatted += f"\n{i}. **{song['title']}** by *{song['artist']}*\n"
        formatted += f"   - Genre: {song['genre']} | Mood: {song['mood']} | Energy: {song['energy']:.1f}\n"
        formatted += f"   - Why it fits: {rec['detailed_explanation'][:200]}...\n"

    return formatted


def create_chat_interface(songs: List[Dict], openai_api_key: str = ""):
    """Create the Gradio chat interface."""

    agent = create_music_chat_agent(songs, openai_api_key)

    def chat_response(message: str, history: List) -> Tuple[str, List]:
        """Process chat message and return response."""
        if not message or not message.strip():
            return "", history

        # Process message through agent
        try:
            result = agent.process_message(message)

            # Format response
            response = result["response"]

            # Add recommendations if any
            if result["recommendations"]:
                response += format_recommendations(result["recommendations"])

            # Append to history in Gradio-compatible format
            history.append({
                "role": "user",
                "content": message
            })
            history.append({
                "role": "assistant",
                "content": response
            })
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            history.append({
                "role": "user",
                "content": message
            })
            history.append({
                "role": "assistant",
                "content": error_msg
            })

        return "", history

    def clear_chat():
        """Clear chat history and agent memory."""
        agent.clear_memory()
        return []

    def get_taste_summary():
        """Get user's taste summary."""
        summary = agent.get_user_taste_summary()

        summary_text = "**Your Music Taste Summary:**\n\n"
        summary_text += f"**Genres mentioned:** {', '.join(summary['mentioned_genres']) or 'None yet'}\n"
        summary_text += f"**Moods mentioned:** {', '.join(summary['mentioned_moods']) or 'None yet'}\n"
        summary_text += f"**Energy preferences:** {', '.join(set(summary['energy_preferences'])) or 'None yet'}\n"
        summary_text += f"**Conversation length:** {summary['conversation_length']} messages\n"

        return summary_text

    # Create Gradio interface
    with gr.Blocks(title="TuneVision AI - Music Recommendation Chat", theme=gr.themes.Soft()) as interface:

        gr.Markdown("# 🎵 TuneVision AI")
        gr.Markdown("Chat with an AI music recommender! Tell me about your mood, favorite genres, or what you're looking for.")

        chatbot = gr.Chatbot(
            height=400,
            label="Chat",
            type="messages"
        )

        with gr.Row():
            msg = gr.Textbox(
                placeholder="Tell me what kind of music you're in the mood for...",
                label="Your Message",
                lines=1
            )
            submit_btn = gr.Button("Send")

        with gr.Row():
            clear_btn = gr.Button("Clear Chat", variant="secondary")
            summary_btn = gr.Button("My Taste Summary", variant="secondary")

        summary_output = gr.Markdown(visible=False)

        # Event handlers
        msg.submit(chat_response, inputs=[msg, chatbot], outputs=[msg, chatbot])
        submit_btn.click(chat_response, inputs=[msg, chatbot], outputs=[msg, chatbot])

        clear_btn.click(clear_chat, outputs=chatbot)

        summary_btn.click(
            get_taste_summary,
            outputs=summary_output
        ).then(
            lambda: gr.update(visible=True),
            outputs=summary_output
        )

    return interface


def launch_chat_interface(data_path: str = "data/songs.csv", openai_api_key: str = ""):
    """Launch the chat interface."""

    # Load songs
    songs = load_songs(data_path)

    # Create and launch interface
    interface = create_chat_interface(songs, openai_api_key)

    interface.launch(
        server_name="0.0.0.0",
        server_port=None,  # Let Gradio find an available port
        share=False,
        show_error=False  # Don't show connection errors
    )


if __name__ == "__main__":
    # Get API key from environment
    api_key = os.getenv("OPENAI_API_KEY", "")

    if not api_key:
        print("Warning: OPENAI_API_KEY not set. Chat functionality will be limited.")

    launch_chat_interface(openai_api_key=api_key)