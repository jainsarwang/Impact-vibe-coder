document.addEventListener('DOMContentLoaded', function() {
    const noteInput = document.getElementById('note-input');
    const addButton = document.getElementById('add-button');
    const notesArea = document.getElementById('notes-area');

    // Load notes from local storage
    loadNotes();

    // Add new note
    addButton.addEventListener('click', addNote);

    function addNote() {
        const noteText = noteInput.value.trim();
        if (noteText !== '') {
            createNoteElement(noteText);
            saveNotes();
            noteInput.value = ''; // Clear the input
        }
    }

    function createNoteElement(noteText) {
        const noteDiv = document.createElement('div');
        noteDiv.classList.add('note');
        noteDiv.textContent = noteText;
        notesArea.appendChild(noteDiv);
    }

    function saveNotes() {
        const notes = [];
        const noteElements = document.querySelectorAll('.note');
        noteElements.forEach(note => {
            notes.push(note.textContent);
        });
        localStorage.setItem('notes', JSON.stringify(notes));
    }

    function loadNotes() {
        const storedNotes = localStorage.getItem('notes');
        if (storedNotes) {
            const notes = JSON.parse(storedNotes);
            notes.forEach(noteText => {
                createNoteElement(noteText);
            });
        }
    }
});