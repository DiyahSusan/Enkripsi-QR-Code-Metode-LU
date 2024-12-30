import numpy as np
from scipy.linalg import lu
import qrcode
import cv2
from PIL import Image

def generate_qr_code(data):
    # generate qr based on input
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H)
    qr.add_data(data)
    qr.make(fit=True)
    qr_matrix = np.array(qr.modules).astype(np.uint8)
    return qr_matrix

def pad_matrix(matrix):
    #memastikan dimensi genap
    rows, cols = matrix.shape
    pad_rows = (2 - (rows % 2)) % 2
    pad_cols = (2 - (cols % 2)) % 2
    
    if pad_rows > 0 or pad_cols > 0:
        padded = np.pad(matrix, ((0, pad_rows), (0, pad_cols)), mode='constant', constant_values=0)
    else:
        padded = matrix.copy()
    
    assert padded.shape[0] % 2 == 0 and padded.shape[1] % 2 == 0
    return padded

def split_into_blocks(matrix):
    rows, cols = matrix.shape
    
    if rows % 2 != 0 or cols % 2 != 0:
        raise ValueError(f"Matrix dimensions must be even. Current shape: {matrix.shape}")
    
    blocks = []
    for i in range(0, rows, 2):
        for j in range(0, cols, 2):
            block = matrix[i:i+2, j:j+2]
            block = block.astype(np.float64) + np.eye(2) * 1e-10
            blocks.append((block, (i, j)))
    return blocks

def lu_encrypt_block(block):
    try:
        P, L, U = lu(block)
        return {"P": P, "L": L, "U": U}
    except np.linalg.LinAlgError as e:
        print(f"Error in LU decomposition: {e}")
        print(f"Problematic block:\n{block}")
        raise

def save_encrypted_data(encrypted_data, image_filename="encrypted_qr.png"):
    blocks = encrypted_data["blocks"]
    padded_shape = encrypted_data["padded_shape"]

    # matriks yang menyimpan komponen enkripsi    
    encrypted_matrix = np.zeros((padded_shape[0]*2, padded_shape[1]*2, 3))
    
    for (block_data, (i, j)) in blocks:
        P, L, U = block_data["P"], block_data["L"], block_data["U"]
        row_start = i*2
        col_start = j*2
        
     
        P_scaled = (P + 1) * 127.5
        L_scaled = (L + 1) * 127.5
        U_scaled = (U + 1) * 127.5
        
        encrypted_matrix[row_start:row_start+2, col_start:col_start+2, 0] = P_scaled
        encrypted_matrix[row_start:row_start+2, col_start:col_start+2, 1] = L_scaled
        encrypted_matrix[row_start:row_start+2, col_start:col_start+2, 2] = U_scaled

    encrypted_image = np.clip(encrypted_matrix, 0, 255).astype(np.uint8)
    Image.fromarray(encrypted_image).save(image_filename, format='PNG')
    
    shapes = {
        "original_shape": encrypted_data["original_shape"],
        "padded_shape": encrypted_data["padded_shape"]
    }
    np.save(image_filename + "_shapes.npy", shapes)

def load_encrypted_data_from_image(image_filename="encrypted_qr.png"):
    # mengolah encrypted image
    encrypted_image = np.array(Image.open(image_filename))
    
    try:
        shapes = np.load(image_filename + "_shapes.npy", allow_pickle=True).item()
        original_shape = shapes["original_shape"]
        padded_shape = shapes["padded_shape"]
    except FileNotFoundError:
        rows, cols, _ = encrypted_image.shape
        padded_shape = (rows // 2, cols // 2)
        original_shape = padded_shape
    
    # ekstraksi dari encrypted image
    blocks = []
    for i in range(0, padded_shape[0], 2):
        for j in range(0, padded_shape[1], 2):
            row_start = i*2
            col_start = j*2
            
            # ekstraksi
            P = encrypted_image[row_start:row_start+2, col_start:col_start+2, 0].astype(np.float64)
            L = encrypted_image[row_start:row_start+2, col_start:col_start+2, 1].astype(np.float64)
            U = encrypted_image[row_start:row_start+2, col_start:col_start+2, 2].astype(np.float64)
            
            # rescale
            P = (P / 127.5) - 1
            L = (L / 127.5) - 1
            U = (U / 127.5) - 1
            
            block_data = {"P": P, "L": L, "U": U}
            blocks.append((block_data, (i, j)))
    
    return {
        "blocks": blocks,
        "original_shape": original_shape,
        "padded_shape": padded_shape
    }

def lu_decrypt_block(encrypted_block):
    P = encrypted_block["P"]
    L = encrypted_block["L"]
    U = encrypted_block["U"]
    
    reconstructed = np.dot(L.astype(np.float64), U.astype(np.float64))
    reconstructed = np.dot(P.T.astype(np.float64), reconstructed)
    reconstructed = reconstructed - np.eye(2) * 1e-10
    
    threshold = 0.5
    return (reconstructed > threshold).astype(np.uint8)

def lu_encrypt(qr_matrix):
    
    padded_matrix = pad_matrix(qr_matrix)
    
    blocks = split_into_blocks(padded_matrix)
    
    encrypted_blocks = []
    for i, (block, position) in enumerate(blocks):
        try:
            encrypted_block = lu_encrypt_block(block)
            encrypted_blocks.append((encrypted_block, position))
        except Exception as e:
            print(f"Error processing block {i} at position {position}: {e}")
            raise
    
    return {
        "blocks": encrypted_blocks,
        "original_shape": qr_matrix.shape,
        "padded_shape": padded_matrix.shape
    }

def lu_decrypt(encryption_data):
    blocks = encryption_data["blocks"]
    padded_shape = encryption_data["padded_shape"]
    original_shape = encryption_data["original_shape"]
    
    reconstructed = np.zeros(padded_shape, dtype=np.uint8)
    
    for encrypted_block, (i, j) in blocks:
        decrypted_block = lu_decrypt_block(encrypted_block)
        reconstructed[i:i+2, j:j+2] = decrypted_block
    
    return reconstructed[:original_shape[0], :original_shape[1]]

def save_qr_image(matrix, filename="qr_code.png"):
    qr_image = (matrix * 255).astype(np.uint8)
    qr_image = cv2.resize(qr_image, (300, 300), interpolation=cv2.INTER_NEAREST)
    Image.fromarray(qr_image).save(filename)

def verify_reconstruction(original, decrypted):
    if original.shape != decrypted.shape:
        print(f"Shape mismatch: Original {original.shape}, Decrypted {decrypted.shape}")
        return False
    
    difference = np.abs(original - decrypted)
    total_diff = np.sum(difference)
    
    
    if total_diff > 0:
        diff_positions = np.where(difference > 0)
        print("\nFirst 5 differences:")
        for i in range(min(5, len(diff_positions[0]))):
            row, col = diff_positions[0][i], diff_positions[1][i]
            print(f"Position ({row}, {col}): Original={original[row, col]}, "
                  f"Decrypted={decrypted[row, col]}")
    
    return total_diff == 0

