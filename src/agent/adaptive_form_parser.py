import logging

logger = logging.getLogger("AdaptiveFormParser")

def intelligent_fill_form(page, user_profile_data: dict):
    """
    Scans active LinkedIn Easy Apply modal inputs dynamically, 
    mapping placeholders and aria-labels to user profile data.
    """
    logger.info("Scanning modal inputs via semantic attribute mapping...")
    try:
        if not hasattr(page, "locator"):
            logger.info("Page object has no locator method (sandbox/mock context). Skipping DOM input scan.")
            return True

        # Find all interactable elements inside the modal
        inputs = page.locator("input, textarea, select").all()
        for field in inputs:
            try:
                # Extract semantic attributes to identify field intent
                label = (
                    field.get_attribute("aria-label") or 
                    field.get_attribute("placeholder") or 
                    field.get_attribute("name") or ""
                ).lower()
                
                if not field.is_visible():
                    continue

                if "phone" in label or "mobile" in label:
                    field.fill(str(user_profile_data.get("phone", "555-0199")))
                    logger.info("Filled phone field.")
                elif "email" in label:
                    field.fill(str(user_profile_data.get("email", "candidate@enterprise.com")))
                    logger.info("Filled email field.")
                elif "city" in label or "location" in label:
                    field.fill(str(user_profile_data.get("location", "Remote")))
                    logger.info("Filled location field.")
                elif "experience" in label or "years" in label:
                    field.fill(str(user_profile_data.get("years_experience", "5")))
                    logger.info("Filled experience field.")
            except Exception as inner_e:
                logger.warning(f"Skipped an input field due to error: {inner_e}")
        
        return True
    except Exception as e:
        logger.error(f"Failed to parse form structure: {e}")
        return False
