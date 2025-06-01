"""
Image Agent - Artistic Visual Creator
Responsible for generating artistic images for each story turn
"""

from crewai import Agent
from openai import OpenAI
import base64
import os
import json
from typing import Dict, List, Any
from datetime import datetime


class ImageAgent:
    """
    The Image Agent creates artistic, consistent visual representations
    of each story turn, maintaining visual continuity and style.
    """
    
    def __init__(self, llm=None):
        self.agent = Agent(
            role='Artistic Visual Creator & Story Illustrator',
            goal='''Create consistent, artistic visual representations of each story 
                    turn that enhance the narrative experience. Maintain visual 
                    continuity while capturing the mood and key elements of each scene.''',
            backstory='''You are a master visual storyteller who understands how to 
                        translate written narrative into compelling artistic imagery. 
                        You have expertise in fantasy art, character design, and 
                        environmental illustration. You excel at maintaining visual 
                        consistency across a story while capturing the unique mood 
                        and atmosphere of each scene. Your art style is painterly 
                        yet detailed, somewhere between realistic and stylized.''',
            verbose=True,
            allow_delegation=False,
            llm=llm
        )
        
        # OpenAI client for image generation
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Visual consistency tracking
        self.visual_history = []
        self.character_appearances = {}
        self.world_style = {}
        self.story_mood_progression = []
        
        # Image storage
        self.images_folder = "story_images"
        self.ensure_images_folder()
        
        # Art style configuration
        self.base_style = """
        Artistic illustration, painterly style, detailed but not photorealistic,
        fantasy art aesthetic, rich colors, atmospheric lighting,
        somewhere between concept art and storybook illustration
        """
    
    def ensure_images_folder(self):
        """Create images folder if it doesn't exist"""
        if not os.path.exists(self.images_folder):
            os.makedirs(self.images_folder)
    
    def create_scene_image(self, story_content: str, turn_number: int, 
                          location: str, characters_present: List[str],
                          mood: str = "mysterious") -> Dict[str, Any]:
        """
        Generate an artistic image for the current story scene
        
        Args:
            story_content: The current scene description
            turn_number: Current turn number
            location: Current location name
            characters_present: List of characters in the scene
            mood: Emotional tone of the scene
            
        Returns:
            Dictionary with image info and file path
        """
        
        # Generate artistic prompt
        image_prompt = self._create_artistic_prompt(
            story_content, location, characters_present, mood, turn_number
        )
        
        # Generate image using OpenAI
        image_data = self._generate_image_with_openai(image_prompt, turn_number)
        
        # Store image and metadata
        image_info = self._save_image_and_metadata(
            image_data, turn_number, image_prompt, story_content
        )
        
        # Update visual history for consistency
        self._update_visual_history(location, characters_present, mood, image_prompt)
        
        return image_info
    
    def _get_character_consistency(self, characters_present: List[str]) -> str:
        """
        Get consistent character descriptions for the characters present
        """
        descriptions = []
        for char in characters_present:
            if char in self.character_appearances:
                descriptions.append(f"{char}: {self.character_appearances[char]}")
            else:
                descriptions.append(f"{char}: (first appearance, establish look)")
        
        return "; ".join(descriptions) if descriptions else "no established characters"
    
    def _create_artistic_prompt(self, story_content: str, location: str, 
                               characters_present: List[str], mood: str, 
                               turn_number: int) -> str:
        """
        Create a detailed artistic prompt for image generation
        """
        
        # Get consistency information
        location_style = self.world_style.get(location, "")
        character_descriptions = self._get_character_consistency(characters_present)
        
        # Build the prompt using the agent's expertise
        prompt_task = f"""
        Create an artistic image prompt for turn {turn_number} of an interactive fiction story.
        
        Scene Description: {story_content}
        Location: {location}
        Characters Present: {characters_present}
        Scene Mood: {mood}
        
        Visual Consistency Requirements:
        - Location Style: {location_style}
        - Character Appearances: {character_descriptions}
        - Previous Mood Progression: {self.story_mood_progression[-3:]}
        
        Base Art Style: {self.base_style}
        
        Create a detailed prompt that:
        1. Captures the key visual elements of this scene
        2. Maintains consistency with previous images
        3. Reflects the {mood} mood through lighting and composition
        4. Includes specific details about character appearances and poses
        5. Describes the environment and atmosphere
        6. Specifies artistic style and rendering approach
        
        Format: Single paragraph, detailed artistic description
        Focus: Visual storytelling, atmospheric mood, character expressions
        
        Avoid: Photorealistic, anime style, cartoonish
        Aim for: Painterly fantasy art, concept art style, storybook illustration
        """
        
        # This would normally be processed by the CrewAI agent
        # For now, we'll create a structured prompt directly
        return self._build_image_prompt(story_content, location, characters_present, mood)
    
    def _build_image_prompt(self, story_content: str, location: str, 
                           characters_present: List[str], mood: str) -> str:
        """
        Build the actual image generation prompt
        """
        
        # Extract key visual elements from story content
        key_elements = self._extract_visual_elements(story_content)
        
        # Character consistency
        character_descriptions = []
        for char in characters_present:
            if char in self.character_appearances:
                character_descriptions.append(self.character_appearances[char])
            else:
                # First appearance - establish look
                char_desc = f"{char} (to be established consistently)"
                character_descriptions.append(char_desc)
        
        # Mood-based lighting and atmosphere
        mood_styles = {
            "mysterious": "dim, moody lighting with deep shadows, atmospheric mist",
            "ominous": "dark, foreboding atmosphere with dramatic lighting",
            "cheerful": "bright, warm lighting with golden tones",
            "tense": "sharp contrasts, dynamic shadows, heightened drama",
            "peaceful": "soft, gentle lighting with harmonious colors",
            "magical": "ethereal glow, shimmering effects, mystical atmosphere"
        }
        
        lighting = mood_styles.get(mood, "balanced, atmospheric lighting")
        
        # Construct the final prompt
        prompt = f"""
        {self.base_style}
        
        Scene: {key_elements}
        Location: {location} with {lighting}
        Characters: {', '.join(character_descriptions) if character_descriptions else 'no characters visible'}
        
        Composition: {self._get_composition_style(mood)}
        Art style: Detailed fantasy illustration, painterly technique, 
        rich color palette, atmospheric perspective, storybook quality
        
        Mood: {mood} atmosphere with appropriate emotional tone
        """
        
        return prompt.strip()
    
    def _extract_visual_elements(self, story_content: str) -> str:
        """Extract key visual elements from story text"""
        # Simple keyword extraction (could be enhanced with NLP)
        visual_keywords = []
        
        # Look for visual descriptors
        visual_words = [
            "tower", "forest", "door", "light", "shadow", "mist", "stone", 
            "ancient", "crumbling", "glowing", "dark", "bright", "magical"
        ]
        
        for word in visual_words:
            if word.lower() in story_content.lower():
                visual_keywords.append(word)
        
        return ", ".join(visual_keywords) if visual_keywords else "fantasy scene"
    
    def _get_composition_style(self, mood: str) -> str:
        """Get composition style based on mood"""
        compositions = {
            "mysterious": "low angle with dramatic shadows",
            "ominous": "high contrast with threatening silhouettes", 
            "cheerful": "balanced composition with open spaces",
            "tense": "dynamic diagonal lines and close framing",
            "peaceful": "harmonious balance with soft edges",
            "magical": "ethereal composition with focal light sources"
        }
        return compositions.get(mood, "balanced artistic composition")
    
    def _generate_image_with_openai(self, prompt: str, turn_number: int) -> Dict[str, Any]:
        """
        Generate image using OpenAI's new GPT-Image-1 model via Responses API
        """
        try:
            # Use the new Responses API with GPT-Image-1
            response = self.openai_client.responses.create(
                model="gpt-4.1-mini",  # Mainline model that supports image generation tool
                input=f"Generate an artistic image: {prompt}",
                tools=[{
                    "type": "image_generation",
                    "size": "1024x1024",
                    "quality": "high",  # high quality for better artistic results
                    "background": "auto",  # let model decide
                    "moderation": "auto"  # standard filtering
                }],
            )
            
            # Extract image data from the new response format
            image_data = [
                output.result
                for output in response.output
                if output.type == "image_generation_call"
            ]
            
            if image_data:
                image_base64 = image_data[0]
                
                # Get revised prompt if available
                revised_prompt = None
                for output in response.output:
                    if output.type == "image_generation_call" and hasattr(output, 'revised_prompt'):
                        revised_prompt = output.revised_prompt
                        break
                
                return {
                    "success": True,
                    "image_base64": image_base64,
                    "revised_prompt": revised_prompt or "No revised prompt available",
                    "original_prompt": prompt,
                    "turn_number": turn_number
                }
            else:
                return {
                    "success": False,
                    "error": "No image data returned from API",
                    "turn_number": turn_number
                }
            
        except Exception as e:
            print(f"❌ Image generation failed for turn {turn_number}: {e}")
            return {
                "success": False,
                "error": str(e),
                "turn_number": turn_number
            }
    
    def _save_image_and_metadata(self, image_data: Dict, turn_number: int, 
                                prompt: str, story_content: str) -> Dict[str, Any]:
        """
        Save image and metadata to files
        """
        if not image_data.get("success"):
            return image_data
        
        try:
            # Save image from base64 data directly (new API returns base64)
            image_base64 = image_data["image_base64"]
            
            # Save image file
            filename = f"turn_{turn_number:03d}.png"
            filepath = os.path.join(self.images_folder, filename)
            
            # Decode and save base64 image
            import base64
            with open(filepath, 'wb') as f:
                f.write(base64.b64decode(image_base64))
            
            # Save metadata
            metadata = {
                "turn_number": turn_number,
                "filename": filename,
                "filepath": filepath,
                "original_prompt": prompt,
                "revised_prompt": image_data.get("revised_prompt", ""),
                "story_content": story_content[:500],  # Truncate for storage
                "timestamp": datetime.now().isoformat(),
                "model_used": "gpt-image-1",  # Track which model was used
                "quality": "high"
            }
            
            metadata_file = os.path.join(self.images_folder, f"turn_{turn_number:03d}_metadata.json")
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            print(f"✅ Image saved: {filepath}")
            
            return {
                "success": True,
                "filepath": filepath,
                "filename": filename,
                "metadata": metadata
            }
            
        except Exception as e:
            print(f"❌ Failed to save image for turn {turn_number}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _update_visual_history(self, location: str, characters: List[str], 
                              mood: str, prompt: str):
        """
        Update visual history for consistency tracking
        """
        # Update location style memory
        if location not in self.world_style:
            self.world_style[location] = f"Established in: {prompt[:100]}..."
        
        # Update character appearance memory
        for char in characters:
            if char not in self.character_appearances:
                # Extract character description from prompt
                self.character_appearances[char] = f"Consistent appearance established"
        
        # Update mood progression
        self.story_mood_progression.append(mood)
        if len(self.story_mood_progression) > 10:
            self.story_mood_progression = self.story_mood_progression[-10:]
        
        # Add to visual history
        self.visual_history.append({
            "location": location,
            "characters": characters,
            "mood": mood,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_image_summary(self) -> Dict[str, Any]:
        """
        Get summary of all generated images
        """
        return {
            "total_images": len(self.visual_history),
            "locations_visited": list(self.world_style.keys()),
            "characters_established": list(self.character_appearances.keys()),
            "mood_progression": self.story_mood_progression,
            "images_folder": self.images_folder
        }
    
    def prepare_for_artbook(self) -> List[Dict[str, Any]]:
        """
        Prepare image data for artbook generation
        """
        artbook_data = []
        
        # Get all metadata files
        for file in os.listdir(self.images_folder):
            if file.endswith("_metadata.json"):
                metadata_path = os.path.join(self.images_folder, file)
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                    artbook_data.append(metadata)
        
        # Sort by turn number
        artbook_data.sort(key=lambda x: x.get("turn_number", 0))
        
        return artbook_data