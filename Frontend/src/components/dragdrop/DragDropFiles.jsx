import "./dragdrop.css";

export default function DragDropFiles({ file, setFile, accepts }) {
  const handleDrag = (e) => {
    e.preventDefault();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    if (!e.dataTransfer?.files || e.dataTransfer.files.length === 0) return;
    
    // Only the first file is accepted
    const droppedFile = e.dataTransfer.files[0];
    if (accepts.split(",").includes(droppedFile.type)) {
      setFile(droppedFile);
    }
  };

  const handleFiles = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
    }
  };

  const handleRemove = (e) => {
    e.stopPropagation();
    setFile(null);
  };

  return (
    <div className="dragdrop" onDragOver={handleDrag} onDrop={handleDrop}>
      {file ? (
        <div className="preview-container">
          <img
            src={URL.createObjectURL(file)}
            alt="Image preview"
            className="preview-image"
          />
          <button type="button" className="remove-btn" onClick={handleRemove}>
            Change image
          </button>
        </div>
      ) : (
        <>
          <h4>Drag and drop your file.</h4>
          <label htmlFor="upload-files">
            <input
              accept={accepts}
              onChange={handleFiles}
              type="file"
              id="upload-files"
            />
            <div className="upload-btn">Select image</div>
          </label>
        </>
      )}
    </div>
  );
}