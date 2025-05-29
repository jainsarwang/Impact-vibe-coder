def import_export_node(state: State) -> Command[Literal["supervisor"]]:
    """
    Node for the import-export agent that verifies import and export statements of directory structure 
    and verifies the path of import and export statements. 
    Rewrite it in Directory if issues found
    """
    logger.info("import-export agent starting task")
    
    # if directory not foun in state, return to supervisor
    directory_structure = state.get('directory_structure')
    if not directory_structure:
        logging.warning("No Directory Object in State, Going back to supervisor")
        return Command(goto='supervisor')
    
    prompt_vars = {
    "CURRENT_TIME": datetime.now().strftime("%a %b %d %Y %H:%M:%S %z"),
    "directory_structure": directory_structure,
    **state  # Include other state variables
}    

    template = get_prompt_template('import-export')
    system_prompt = PromptTemplate(
        input_variables=["CURRENT_TIME","directory_structure"],
        template=template,
    ).format(**prompt_vars)
    
    
    messages = [
    {
        "role": "system",
        "content": system_prompt
    },
    {
        "role": "user",
        "content": directory_structure
    }
]
        
    llm = get_llm_by_type("basic")
    response = llm.invoke(messages)
    full_response = response.content

    logger.debug(f"Current state messages: {state['messages']}")
    logger.info(f"Code Planner response: {full_response}")

    
    if full_response.startswith("```json"):
        full_response = full_response.removeprefix("```json")

    if full_response.endswith("```"):
        full_response = full_response.removesuffix("```")

    try:
        repaired_response = json_repair.loads(full_response)
        full_response = json.dumps(repaired_response)
        
        with open("directory_structure.json", "w", encoding="utf-8") as f:
            json.dump(repaired_response, f, indent=2, ensure_ascii=False)
    except json.JSONDecodeError:
        logger.warning("Import Export response is not a valid JSON")
        goto = "__end__"

    return Command(
        update={
            "messages": [
                HumanMessage(
                    content=full_response,
                    name="import-export",
                )
            ],
            "directory_structure": repaired_response
        },
        goto="supervisor",
    )